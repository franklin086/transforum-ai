export type PcmWavChunk = {
  blob: Blob;
  durationMs: number;
};

export type PcmWavRecorder = {
  stop: () => void;
};

const TARGET_SAMPLE_RATE = 16000;

function mergeBuffers(buffers: Float32Array[]) {
  const totalLength = buffers.reduce((sum, buffer) => sum + buffer.length, 0);
  const merged = new Float32Array(totalLength);
  let offset = 0;
  for (const buffer of buffers) {
    merged.set(buffer, offset);
    offset += buffer.length;
  }
  return merged;
}

function downsampleBuffer(buffer: Float32Array, sourceSampleRate: number) {
  if (sourceSampleRate === TARGET_SAMPLE_RATE) {
    return buffer;
  }
  const sampleRateRatio = sourceSampleRate / TARGET_SAMPLE_RATE;
  const newLength = Math.max(1, Math.round(buffer.length / sampleRateRatio));
  const result = new Float32Array(newLength);
  let offsetResult = 0;
  let offsetBuffer = 0;

  while (offsetResult < result.length) {
    const nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
    let accumulator = 0;
    let count = 0;
    for (let index = offsetBuffer; index < nextOffsetBuffer && index < buffer.length; index += 1) {
      accumulator += buffer[index];
      count += 1;
    }
    result[offsetResult] = count > 0 ? accumulator / count : 0;
    offsetResult += 1;
    offsetBuffer = nextOffsetBuffer;
  }

  return result;
}

function floatTo16BitPcm(input: Float32Array) {
  const output = new Int16Array(input.length);
  for (let index = 0; index < input.length; index += 1) {
    const sample = Math.max(-1, Math.min(1, input[index]));
    output[index] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
  }
  return output;
}

function writeString(view: DataView, offset: number, value: string) {
  for (let index = 0; index < value.length; index += 1) {
    view.setUint8(offset + index, value.charCodeAt(index));
  }
}

function encodeWav(samples: Float32Array) {
  const pcm = floatTo16BitPcm(samples);
  const buffer = new ArrayBuffer(44 + pcm.length * 2);
  const view = new DataView(buffer);

  writeString(view, 0, "RIFF");
  view.setUint32(4, 36 + pcm.length * 2, true);
  writeString(view, 8, "WAVE");
  writeString(view, 12, "fmt ");
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true);
  view.setUint16(22, 1, true);
  view.setUint32(24, TARGET_SAMPLE_RATE, true);
  view.setUint32(28, TARGET_SAMPLE_RATE * 2, true);
  view.setUint16(32, 2, true);
  view.setUint16(34, 16, true);
  writeString(view, 36, "data");
  view.setUint32(40, pcm.length * 2, true);

  let offset = 44;
  for (let index = 0; index < pcm.length; index += 1, offset += 2) {
    view.setInt16(offset, pcm[index], true);
  }

  return new Blob([view], { type: "audio/wav" });
}

export async function createPcmWavRecorder(options: {
  stream: MediaStream;
  chunkDurationMs: number;
  onChunk: (chunk: PcmWavChunk) => void;
}) {
  const AudioContextClass = window.AudioContext || (window as typeof window & { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
  if (!AudioContextClass) {
    throw new Error("Web Audio API is not available.");
  }

  const audioContext = new AudioContextClass();
  console.log(`[PCM_RECORDER] audioContext sampleRate=${audioContext.sampleRate}`);
  console.log(`[PCM_RECORDER] chunk_duration_ms=${options.chunkDurationMs}`);
  if (audioContext.state === "suspended") {
    await audioContext.resume();
  }
  const source = audioContext.createMediaStreamSource(options.stream);
  const processor = audioContext.createScriptProcessor(4096, 1, 1);
  let buffers: Float32Array[] = [];
  let stopped = false;

  processor.onaudioprocess = (event) => {
    if (stopped) {
      return;
    }
    const input = event.inputBuffer.getChannelData(0);
    buffers.push(new Float32Array(input));
  };

  source.connect(processor);
  processor.connect(audioContext.destination);

  const flush = () => {
    if (stopped || buffers.length === 0) {
      return;
    }
    const merged = mergeBuffers(buffers);
    buffers = [];
    const downsampled = downsampleBuffer(merged, audioContext.sampleRate);
    const wavBlob = encodeWav(downsampled);
    console.log(`[PCM_RECORDER] wav_blob_size=${wavBlob.size}`);
    options.onChunk({
      blob: wavBlob,
      durationMs: options.chunkDurationMs,
    });
  };

  const intervalId = window.setInterval(flush, options.chunkDurationMs);

  return {
    stop: () => {
      if (stopped) {
        return;
      }
      flush();
      stopped = true;
      window.clearInterval(intervalId);
      processor.disconnect();
      source.disconnect();
      void audioContext.close();
    },
  } satisfies PcmWavRecorder;
}
