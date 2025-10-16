// Initialize Telegram WebApp
const tg = window.Telegram.WebApp
tg.expand()
tg.ready()

// Global state
let currentLang = "ru"
let products = []
let currentCategory = "all"
let isAdmin = false
// translationsData загружается из translations.js

// Check if admin mode
const urlParams = new URLSearchParams(window.location.search)
isAdmin = urlParams.get("admin") === "true"

// Get translation
function t(key) {
  return translationsData[currentLang]?.[key] || key
}

// Update all texts
function updateTexts() {
  document.getElementById("pageTitle").textContent = isAdmin ? t("admin_panel") : t("shop_title")
  document.getElementById("createLotBtn").textContent = t("create_lot")
  document.getElementById("createProductBtn").textContent = t("create_product")
  document.getElementById("allProductsBtn").textContent = t("all_products")
  document.getElementById("createProductTitle").textContent = t("create_product")
  document.getElementById("createLotTitle").textContent = t("create_lot")
  document.getElementById("labelProductName").textContent = t("product_name")
  document.getElementById("labelProductPrice").textContent = t("product_price")
  document.getElementById("labelCategory").textContent = t("categories")
  document.getElementById("labelFloat").textContent = t("float_value")
  document.getElementById("labelDescription").textContent = t("product_description")
  document.getElementById("labelPhoto").textContent = t("product_photo")
  document.getElementById("labelLink").textContent = t("product_link")
  document.getElementById("saveProductBtn").textContent = t("save")
  document.getElementById("labelLotName").textContent = t("product_name")
  document.getElementById("labelStartingPrice").textContent = t("starting_price")
  document.getElementById("labelLotCategory").textContent = t("categories")
  document.getElementById("labelLotFloat").textContent = t("float_value")
  document.getElementById("labelLotDescription").textContent = t("product_description")
  document.getElementById("labelLotPhoto").textContent = t("product_photo")
  document.getElementById("labelLotLink").textContent = t("product_link")
  document.getElementById("saveLotBtn").textContent = t("save")

  renderCategories()
  renderProducts()
}

// Language switcher
document.querySelectorAll(".lang-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".lang-btn").forEach((b) => b.classList.remove("active"))
    btn.classList.add("active")
    currentLang = btn.dataset.lang
    updateTexts()
  })
})

// Render categories
function renderCategories() {
  const categoriesDiv = document.getElementById("categories")
  const categories = [
    { id: "all", name: t("all_categories") },
    { id: "weapons", name: t("weapons") },
    { id: "agents", name: t("agents") },
  ]

  categoriesDiv.innerHTML = categories
    .map(
      (cat) => `
        <button class="category-btn ${currentCategory === cat.id ? "active" : ""}" 
                onclick="filterByCategory('${cat.id}')">
            ${cat.name}
        </button>
    `,
    )
    .join("")
}

// Filter by category
function filterByCategory(category) {
  currentCategory = category
  renderCategories()
  renderProducts()
}

// Render products
function renderProducts() {
  const grid = document.getElementById("productsGrid")
  const filteredProducts =
    currentCategory === "all"
      ? products.filter((p) => p.status === "available")
      : products.filter((p) => p.category === currentCategory && p.status === "available")

  if (filteredProducts.length === 0) {
    grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📦</div>
                <p>${t("no_products")}</p>
            </div>
        `
    return
  }

  grid.innerHTML = filteredProducts
    .map(
      (product) => `
        <div class="product-card">
            <img src="${product.photo_url}" alt="${product.name}" class="product-image" 
                 onerror="this.src='https://via.placeholder.com/400x200/667eea/ffffff?text=Product'">
            <div class="product-info">
                <div class="product-header">
                    <div>
                        <div class="product-name">${product.name}</div>
                        <div class="product-category">${t(product.category)}</div>
                    </div>
                </div>
                <div class="product-price">${product.price} ₽</div>
                ${product.float ? `<div class="product-float">Float: ${product.float}</div>` : ""}
                <div class="product-description">${product.description}</div>
                <span class="product-status status-${product.status}">${t(product.status)}</span>
                <div class="product-actions">
                    <button class="btn btn-primary" onclick="buyProduct('${product.id}', '${product.link}')">
                        ${t("buy")}
                    </button>
                    <button class="btn btn-secondary" onclick="copyLink('${product.link}')">
                        ${t("copy_link")}
                    </button>
                    <button class="btn btn-secondary" onclick="contactAdmin()">
                        ${t("contact_admin")}
                    </button>
                </div>
            </div>
        </div>
    `,
    )
    .join("")
}

// Buy product
function buyProduct(productId, link) {
  tg.sendData(`buy:${productId}`)
  tg.openLink(link)
}

// Copy link
function copyLink(link) {
  navigator.clipboard.writeText(link).then(() => {
    tg.showAlert(t("link_copied"))
  })
}

// Contact admin
function contactAdmin() {
  tg.openTelegramLink("https://t.me/admin") // Replace with actual admin username
}

// Modal functions
function openCreateProductModal() {
  document.getElementById("createProductModal").classList.add("active")
}

function openCreateLotModal() {
  document.getElementById("createLotModal").classList.add("active")
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove("active")
}

// Show/hide float field based on category
document.getElementById("productCategory")?.addEventListener("change", (e) => {
  const floatGroup = document.getElementById("floatGroup")
  floatGroup.style.display = e.target.value === "weapons" ? "block" : "none"
})

document.getElementById("lotCategory")?.addEventListener("change", (e) => {
  const floatGroup = document.getElementById("lotFloatGroup")
  floatGroup.style.display = e.target.value === "weapons" ? "block" : "none"
})

// Create product form
document.getElementById("createProductForm")?.addEventListener("submit", (e) => {
  e.preventDefault()
  const formData = {
    name: document.getElementById("productName").value,
    price: Number.parseFloat(document.getElementById("productPrice").value),
    category: document.getElementById("productCategory").value,
    description: document.getElementById("productDescription").value,
    photo_url: document.getElementById("productPhoto").value,
    link: document.getElementById("productLink").value,
    float: document.getElementById("productFloat").value || null,
    status: "available",
    id: Date.now().toString(),
  }

  products.push(formData)
  tg.sendData("admin:product_created")
  closeModal("createProductModal")
  renderProducts()
  e.target.reset()
})

// Create lot form
document.getElementById("createLotForm")?.addEventListener("submit", (e) => {
  e.preventDefault()
  tg.sendData("admin:auction_created")
  closeModal("createLotModal")
  e.target.reset()
})

// Show all products (admin)
function showAllProducts() {
  const grid = document.getElementById("adminProductsGrid")
  grid.innerHTML = products
    .map(
      (product) => `
        <div class="product-card">
            <img src="${product.photo_url}" alt="${product.name}" class="product-image"
                 onerror="this.src='https://via.placeholder.com/400x200/667eea/ffffff?text=Product'">
            <div class="product-info">
                <div class="product-name">${product.name}</div>
                <div class="product-category">${t(product.category)}</div>
                <div class="product-price">${product.price} ₽</div>
                ${product.float ? `<div class="product-float">Float: ${product.float}</div>` : ""}
                <span class="product-status status-${product.status}">${t(product.status)}</span>
                <div class="product-actions">
                    <button class="btn btn-secondary" onclick="toggleStatus('${product.id}')">
                        ${t("change_status")}
                    </button>
                    <button class="btn btn-danger" onclick="deleteProduct('${product.id}')">
                        ${t("delete")}
                    </button>
                </div>
            </div>
        </div>
    `,
    )
    .join("")
}

// Toggle product status
function toggleStatus(productId) {
  const product = products.find((p) => p.id === productId)
  if (product) {
    product.status = product.status === "available" ? "sold" : "available"
    tg.sendData("admin:status_changed")
    showAllProducts()
    renderProducts()
  }
}

// Delete product
function deleteProduct(productId) {
  if (confirm(t("confirm_delete"))) {
    products = products.filter((p) => p.id !== productId)
    tg.sendData("admin:product_deleted")
    showAllProducts()
    renderProducts()
  }
}

// Initialize
function init() {
  // Mock data for demonstration
  products = [
    {
      id: "1",
      name: "AK-47 | Redline",
      price: 2500,
      category: "weapons",
      description: "Field-Tested качество, отличное состояние",
      photo_url: "https://via.placeholder.com/400x200/667eea/ffffff?text=AK-47",
      link: "https://example.com/item1",
      float: 0.25,
      status: "available",
    },
    {
      id: "2",
      name: "Агент Phoenix",
      price: 1500,
      category: "agents",
      description: "Редкий агент из коллекции",
      photo_url: "https://via.placeholder.com/400x200/764ba2/ffffff?text=Agent",
      link: "https://example.com/item2",
      status: "available",
    },
  ]

  if (isAdmin) {
    document.getElementById("shopView").style.display = "none"
    document.getElementById("adminPanel").classList.add("active")
  } else {
    renderProducts()
  }

  updateTexts()
}

init()
