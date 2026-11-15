function addRow(body, values) {
  const tr = document.createElement("tr");
  for (const text of values) {
    const td = document.createElement("td");
    td.textContent = text;
    tr.appendChild(td);
  }
  body.appendChild(tr);
}

async function loadHistory() {
  try {
    const response = await fetch("/api/history");
    if (response.status === 401) {
      window.location.href = "/login";
      return;
    }
    const data = await response.json();
    const tBody = document.querySelector("#transactions-table tbody");
    for (const t of data.transactions) {
      addRow(tBody, [t.created_at, t.from_currency, t.to_currency, formatMoney(t.amount, t.from_currency), t.rate_used, formatMoney(t.fee_usd, "USD"), formatMoney(t.converted_amount, t.to_currency)]);
    }
    const qBody = document.querySelector("#quotes-table tbody");
    for (const q of data.quotes) {
      const best = q.results.find(r => r.scenario === "max" && r.years === 10);
      const worst = q.results.find(r => r.scenario === "min" && r.years === 10);
      addRow(qBody, [q.created_at, q.plan_name, formatMoney(q.lump_sum, "GBP"), formatMoney(q.monthly_amount, "GBP"), formatMoney(best.final_value, "GBP"), formatMoney(worst.final_value, "GBP")]);
    }
  } catch (problem) {
    showMessage("error", "Could not load your history. Please try again.");
  }
}

loadHistory();
