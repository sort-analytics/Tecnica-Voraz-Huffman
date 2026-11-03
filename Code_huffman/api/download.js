export default async function handler(req, res) {
  const targetUrl = req.query.url;
  if (!targetUrl) {
    return res.status(400).send("Falta el parámetro url");
  }

  try {
    const cleanUrl = targetUrl.replace(/^http:/, "https:");
    const response = await fetch(cleanUrl, {
      headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HuffmanCompressor/1.0",
      },
    });

    if (!response.ok) {
      return res.status(response.status).send(`Error HTTP ${response.status}`);
    }

    const arrayBuffer = await response.arrayBuffer();
    const buffer = Buffer.from(arrayBuffer);

    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Content-Type", "application/octet-stream");
    return res.status(200).send(buffer);
  } catch (error) {
    return res.status(500).send(error.message);
  }
}
