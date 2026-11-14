async function loadCurrencies() {
  const response = await fetch("/api/currencies");
  const currencies = await response.json();
  for (const select of document.querySelectorAll(".currency-list")) {
    for (const item of currencies) {
      const option = document.createElement("option");
      option.value = item.code;
      option.textContent = item.code + " - " + item.name;
      select.appendChild(option);
    }
  }
  document.getElementById("from").value = "GBP";
  document.getElementById("to").value = "USD";
}

async function handleConvert(event) {
  event.preventDefault();
  showMessage("error", "");
  showMessage("warning", "");
  showMessage("result", "");
  const body = {
    amount: document.getElementById("amount").value,
    from: document.getElementById("from").value,
    to: document.getElementById("to").value,
  };
  cacheForm("converter", body);
  try {
    const reply = await postJson("/api/convert", body);
    if (!reply.ok) {
      showMessage("error", reply.data.error);
      return;
    }
    const d = reply.data;
    showMessage("result", formatMoney(d.amount, d.from) + " = " + formatMoney(d.converted, d.to) + " at rate " + d.rate + ". Fee: " + formatMoney(d.fee_usd, "USD") + " (" + d.fee_percent + "%).");
    if (d.warning) {
      showMessage("warning", d.warning);
    }
    clearCachedForm("converter");
  } catch (problem) {
    showMessage("error", "Could not reach the server. Your entries are saved on this device; try again shortly.");
  }
}

async function startConverter() {
  await loadCurrencies();
  const saved = restoreForm("converter");
  if (saved) {
    document.getElementById("amount").value = saved.amount;
    document.getElementById("from").value = saved.from;
    document.getElementById("to").value = saved.to;
  }
  document.getElementById("convert-form").addEventListener("submit", handleConvert);
}

startConverter();