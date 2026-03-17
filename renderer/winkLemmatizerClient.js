export class WinkLemmatizerClient {
  constructor(workerUrl) {
    this.worker = new Worker(workerUrl, { type: "module" });
    this.seq = 0;
    this.pending = new Map();

    this.worker.onmessage = (event) => {
      const { id, ok, payload } = event.data || {};
      const task = this.pending.get(id);
      if (!task) return;

      this.pending.delete(id);
      if (ok) {
        task.resolve(payload);
      } else {
        task.reject(payload);
      }
    };
  }

  lemmatizeInSentence(sentence, targetWord) {
    const id = ++this.seq;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.worker.postMessage({ id, sentence, target_word: targetWord });
    });
  }

  dispose() {
    this.worker.terminate();
    this.pending.clear();
  }
}