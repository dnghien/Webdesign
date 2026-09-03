const fetchBtn = document.querySelector("#fetch-users");
const tbody = document.querySelector("#user-table-body");

fetchBtn.addEventListener("click", () => {
    fetch("https://jsonplaceholder.typicode.com/users")
        .then(response => {
            if (!response.ok) {
                throw new Error("Failed to fetch users");
            }
            return response.json();
        })
        .then(users => {
            tbody.innerHTML = "";

            users.forEach(user => {
                const address = user.address
                    ? `${user.address.street}, ${user.address.city}`
                    : "N/A";

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${user.id}</td>
                    <td>${user.name}</td>
                    <td>${user.phone}</td>
                    <td>${user.email}</td>
                    <td><a href="https://${user.website}" target="_blank">${user.website}</a></td>
                    <td>${address}</td>
                `;
                tbody.appendChild(row);
            });
        })
        .catch(error => {
            console.error("Error fetching users:", error);
            tbody.innerHTML = `<tr><td colspan="5">Failed to load users.</td></tr>`;
        });
});