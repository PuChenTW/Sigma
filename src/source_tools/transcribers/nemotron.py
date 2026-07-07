import asyncio
import subprocess
import wave

NEMOTRON_MAX_BYTES = 2_000_000_000
SAMPLE_RATE = 16_000


class NemotronTranscriber:
    accepted_formats = ("wav",)
    max_bytes = NEMOTRON_MAX_BYTES

    def __init__(self, model_dir: str, language: str = "auto", num_threads: int = 4) -> None:
        self._model_dir = model_dir
        self._language = language
        self._num_threads = num_threads
        self._recognizer = None

    def _get_recognizer(self):
        if self._recognizer is None:
            import sherpa_onnx

            self._recognizer = sherpa_onnx.OnlineRecognizer.from_transducer(
                tokens=f"{self._model_dir}/tokens.txt",
                encoder=f"{self._model_dir}/encoder.int8.onnx",
                decoder=f"{self._model_dir}/decoder.int8.onnx",
                joiner=f"{self._model_dir}/joiner.int8.onnx",
                num_threads=self._num_threads,
                model_type="nemo_transducer",
                provider="cpu",
            )
        return self._recognizer

    async def transcribe_chunk(self, path: str) -> str:
        return await asyncio.to_thread(self._run, path)

    def _run(self, path: str) -> str:
        import numpy as np

        samples = self._read_16k_mono(path)
        rec = self._get_recognizer()
        stream = rec.create_stream()
        if stream.has_option("language"):
            stream.set_option("language", self._language)
        stream.accept_waveform(SAMPLE_RATE, samples)
        stream.accept_waveform(SAMPLE_RATE, np.zeros(SAMPLE_RATE // 2, dtype=np.float32))
        stream.input_finished()
        while rec.is_ready(stream):
            rec.decode_stream(stream)
        return rec.get_result(stream).strip()

    def _read_16k_mono(self, path: str):
        import io

        import numpy as np

        proc = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ar", str(SAMPLE_RATE), "-ac", "1", "-f", "wav", "-"], capture_output=True)
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg decode failed: {proc.stderr.decode('utf-8', 'replace')[:200]}")
        with wave.open(io.BytesIO(proc.stdout)) as wav:
            frames = wav.readframes(wav.getnframes())
        return np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0
