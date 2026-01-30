(function () {
  // Floating button
  const btn = document.createElement("button");
  btn.innerText = "💬";
  Object.assign(btn.style, {
    position: "fixed",
    bottom: "20px",
    right: "20px",
    width: "60px",
    height: "60px",
    borderRadius: "50%",
    background: "#4c1d95",
    color: "white",
    border: "none",
    fontSize: "26px",
    cursor: "pointer",
    zIndex: "9999",
    boxShadow: "0 4px 15px rgba(0,0,0,0.3)"
  });

  // Chat window
  const box = document.createElement("div");
  Object.assign(box.style, {
    position: "fixed",
    bottom: "90px",
    right: "20px",
    width: "380px",
    height: "550px",
    background: "white",
    borderRadius: "14px",
    display: "none",
    flexDirection: "column",
    zIndex: "9999",
    boxShadow: "0 8px 25px rgba(0,0,0,0.3)",
    overflow: "hidden"
  });

  // Header
  const header = document.createElement("div");
  header.innerHTML = "🤖 Hackathon Assistant <span style='cursor:pointer'>✖</span>";
  Object.assign(header.style, {
    background: "#4c1d95",
    color: "white",
    padding: "12px",
    fontWeight: "bold",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center"
  });

  // Chat iframe
  const iframe = document.createElement("iframe");
  iframe.src = "/chatbot/chatbot.html";
  Object.assign(iframe.style, {
    border: "none",
    width: "100%",
    height: "100%"
  });

  box.appendChild(header);
  box.appendChild(iframe);
  document.body.appendChild(btn);
  document.body.appendChild(box);

  btn.onclick = () => {
    box.style.display = box.style.display === "flex" ? "none" : "flex";
  };

  header.onclick = () => {
    box.style.display = "none";
  };
})();
