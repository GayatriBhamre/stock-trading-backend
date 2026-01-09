const API = "http://127.0.0.1:5000";

// Load balance
function loadBalance() {
    fetch(`${API}/api/balance`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("balance").innerText = "₹ " + data.balance;
        });
}

// Load stocks
function loadStocks() {
    fetch(`${API}/api/stocks`)
        .then(res => res.json())
        .then(stocks => {
            let html = "";
            stocks.forEach(stock => {
                html += `
                    <tr>
                        <td>${stock.name}</td>
                        <td>${stock.price}</td>
                        <td>
                            <button onclick="buyStock('${stock.name}')">
                                Buy
                            </button>
                        </td>
                    </tr>
                `;
            });
            document.getElementById("stocks-table").innerHTML = html;
        });
}

// Buy stock
function buyStock(symbol) {
    fetch(`${API}/api/order/buy`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ symbol })
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message || data.error);
        loadBalance();
    });
}

// Add wishlist
function addWishlist() {
    const symbol = document.getElementById("symbol").value;
    const target = document.getElementById("target").value;

    fetch(`${API}/api/wishlist`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            symbol,
            target_price: Number(target)
        })
    })
    .then(res => res.json())
    .then(data => alert(data.message));
}

// Initial load
loadBalance();
loadStocks();
