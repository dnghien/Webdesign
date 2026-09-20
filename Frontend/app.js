const API_BASE = window.location.protocol === "file:" ? "http://localhost:8000" : "";

const form = document.getElementById("item-form");
const submitBtn = document.getElementById("submit-btn");
const cancelBtn = document.getElementById("cancel-btn");
const messageBox = document.getElementById("message");
let editingId = null;

function showMessage(text, isError = false) {
    if (!messageBox) return;
    messageBox.textContent = text;
    messageBox.style.color = isError ? "#b91c1c" : "#166534";
    messageBox.style.display = "block";
}

function resetForm() {
    if (!form) return;
    form.reset();
    editingId = null;
    if (submitBtn) submitBtn.textContent = "Add";
}

if (cancelBtn) {
    cancelBtn.addEventListener("click", resetForm);
}

if (form) {
    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const name = document.getElementById("name").value.trim();
        const price = Number(document.getElementById("price").value);

        if (!name || Number.isNaN(price) || price < 0) {
            showMessage("Vui lòng nhập tên và giá hợp lệ.", true);
            return;
        }

        try {
            const method = editingId !== null ? "PUT" : "POST";
            const url = editingId !== null ? `/items/${editingId}` : "/items";

            const response = await fetch(`${API_BASE}${url}`, {
                method,
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ name, price })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || "Không thể lưu dữ liệu");
            }

            const wasEditing = editingId !== null;
            await fetchData();
            resetForm();
            showMessage(wasEditing ? "Cập nhật thành công." : "Thêm thành công.");
        } catch (err) {
            console.error(err);
            showMessage(err.message || "Có lỗi khi lưu dữ liệu.", true);
        }
    });
}

async function fetchData() {
    const tbody = document.querySelector("tbody");
    if (!tbody) {
        console.error("tbody not found");
        return null;
    }

    try {
        const response = await fetch(`${API_BASE}/items`);
        if (!response.ok) {
            throw new Error("Không thể tải dữ liệu");
        }

        const data = await response.json();
        const items = data.items;

        tbody.innerHTML = "";

        items.forEach(item => {
            const row = document.createElement("tr");

            row.innerHTML = `
                <td>${item.id}</td>
                <td>${item.name}</td>
                <td>${item.price}</td>
                <td>
                    <button class="edit-btn" data-id="${item.id}">Edit</button>
                    <button class="delete-btn" data-id="${item.id}">Delete</button>
                </td>
            `;

            tbody.appendChild(row);
        });

        document.querySelectorAll(".delete-btn").forEach(button => {
            button.addEventListener("click", async () => {
                const id = Number(button.dataset.id);
                await handleDelete(id);
            });
        });

        document.querySelectorAll(".edit-btn").forEach(button => {
            button.addEventListener("click", async () => {
                const id = Number(button.dataset.id);
                await handleEdit(id);
            });
        });

        return data;
    } catch (err) {
        console.error(err);
        return null;
    }
}

async function handleEdit(id) {
    try {
        const response = await fetch(`${API_BASE}/items/${id}`);
        if (!response.ok) {
            throw new Error("Item not found");
        }

        const item = await response.json();
        document.getElementById("name").value = item.name;
        document.getElementById("price").value = item.price;
        editingId = id;

        if (submitBtn) submitBtn.textContent = "Update";
        showMessage(`Đang chỉnh sửa item #${id}`);
    } catch (err) {
        console.error(err);
        showMessage("Không thể lấy dữ liệu để sửa.", true);
    }
}

async function handleDelete(id) {
    try {
        const response = await fetch(`${API_BASE}/items/${id}`, {
            method: "DELETE",
            headers: {
                "Content-Type": "application/json"
            }
        });

        if (!response.ok) {
            throw new Error("Delete failed");
        }

        if (editingId === id) {
            resetForm();
        }

        await fetchData();
        showMessage("Xóa thành công.");
    } catch (err) {
        console.error(err);
        showMessage("Có lỗi khi xóa dữ liệu.", true);
    }
}

fetchData();