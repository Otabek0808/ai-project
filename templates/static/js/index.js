const menu = document.getElementById("menu");
const menuBox = document.getElementById("menu_box");
const dashboard = document.getElementById("dashboard");
const hedMain = document.getElementById("hedMain");
const menuBtn = document.getElementById("menuBtn");
let isVisible = false;

menu.addEventListener("click", () => {
  if (isVisible) {
    menuBox.style.width = "0"; // Kenglikni 0 ga o'zgartiramiz
    menuBtn.style.opacity = "0";
    setTimeout(() => {
      menuBox.classList.remove("show"); // Ko'rinmas qiladi
      menuBox.style.display = "none"; // Tugal yashirish
      dashboard.style.margin = "-35px auto"; // Dashboard ni asl holatiga qaytaramiz
      hedMain.style.width = "100%";
      menuBtn.style.display = "none";
      menuBtn.classList.remove("show");
    }, 500); // Animatsiya davomiyligi
  } else {
    menuBox.style.display = "block"; // Ko'rsatamiz

    setTimeout(() => {
      menuBox.classList.add("show"); // Ko'rinadigan holatga o'tamiz
      menuBox.style.width = "25%"; // Kenglikni o'zgartiramiz
      dashboard.style.transform = "translateX(320px)"; // Dashboardni chapga suramiz
      hedMain.style.width = "60%";
    }, 10); // Bir oz kutish

    setTimeout(() => {
      menuBtn.style.display = "block"; // `menuBtn` ni ko'rsatamiz
      menuBtn.style.width = "20%"; // Kengligini o'zgartirish
      menuBtn.style.opacity = "1";
    }, 500); // 3 soniya o'tgach
  }

  isVisible = !isVisible; // Mavjudligini o'zgartirish
});

// profil img
const listBtn = document.getElementById("listBtn");
const loginBtn = document.getElementById("loginBtn");

loginBtn.addEventListener("click", () => {
  if (listBtn.classList.contains("visible")) {
    listBtn.classList.remove("visible");
    setTimeout(() => {
      listBtn.classList.add("hidden");
    }, 500); // Kengayish tugagach, yashiradi
  } else {
    listBtn.classList.remove("hidden");
    listBtn.style.transform = "translateX(-250px)";
    setTimeout(() => {
      listBtn.classList.add("visible");
    }, 0); // Darhol ko'rsatadi
  }
});
