const WebSocket = require("ws");

const PORT = Number(process.env.WS_PORT || 3030);
const HOST = process.env.WS_HOST || "127.0.0.1";

const ws = new WebSocket.Server({
  port: PORT,
  host: HOST,
});

ws.on("listening", () => {
  console.log(`WebSocket server listening on ws://${HOST}:${PORT}`);
});

ws.on("error", console.error);

ws.on("connection", function connect(client, req) {
  console.log("client has connected");
  client.classId = "";
  client.route = req.url.replace("/ws/", "");

  client.on("message", (message) => {
    let data;

    try {
      data = JSON.parse(message.toString());
    } catch {
      return;
    }

    if (data.type === "join_class") {
      client.classId = String(data.class_id || "");
      return;
    }

    if (data.type === "chat_message") {
      const classId = String(data.class_id || client.classId || "");

      broadcast({
        type: "new_chat_message",
        class_id: classId,
        post: data.post,
      }, client);
    }
  });

  client.on("close", () => {
    console.log("client has disconnected");
  });
});

function send(client, data) {
  if (client.readyState === WebSocket.OPEN) {
    client.send(JSON.stringify(data));
  }
}

// sends msg to all connected clients in the same class!
function broadcast(data, exceptClient) {
  for (const client of ws.clients) {
    if (client === exceptClient) {
      continue;
    }

    if (client.classId === data.class_id) {
      send(client, data);
    }
  }
}
