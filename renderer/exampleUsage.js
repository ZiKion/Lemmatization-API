import { WinkLemmatizerClient } from "./winkLemmatizerClient.js";

const client = new WinkLemmatizerClient(
  new URL("./winkLemmatizer.worker.js", import.meta.url)
);

async function demo() {
  const result = await client.lemmatizeInSentence(
    "It was a bore to listen to him.",
    "bore"
  );

  console.log(result);
  // => { lemma: "bore", token: "bore" }
}

demo().catch((err) => {
  console.error("Local lemmatization failed:", err);
});