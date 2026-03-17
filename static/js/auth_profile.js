/**
 * Profil sayfasi - form dogrulama, foto yukleme
 */
(function () {
    "use strict";

    var formEl = document.getElementById("profileForm");
    var photoInput = document.getElementById("profilePhotoInput");
    var photoUploadBtn = document.getElementById("profilePhotoUploadBtn");
    var progressDiv = document.getElementById("photoUploadProgress");
    var photoContainer = document.getElementById("profilePhotoContainer");
    var profilePictureInput = document.getElementById("profile_picture");
    var profileDataEl = document.getElementById("profileData");

    function showToast(message, type) {
        var toastEl = document.getElementById("profileToast");
        var toastMessage = document.getElementById("toastMessage");
        var iconEl = toastEl && toastEl.querySelector(".profile-toast-icon");
        if (!toastEl || !toastMessage) return;
        toastMessage.textContent = message;
        if (iconEl) {
            iconEl.className = type === "error" ? "fas fa-exclamation-circle text-danger me-2 profile-toast-icon" : "fas fa-check-circle text-success me-2 profile-toast-icon";
        }
        var toast = new bootstrap.Toast(toastEl);
        toast.show();
    }

    function validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function validatePasswordChange() {
        var current = document.getElementById("current_password").value;
        var newPwd = document.getElementById("new_password").value;
        var confirm = document.getElementById("confirm_password").value;
        if (!newPwd && !confirm && !current) return { ok: true };
        if (!current) {
            showToast("Sifre degistirmek icin mevcut sifrenizi girmelisiniz.", "error");
            return { ok: false };
        }
        if (newPwd !== confirm) {
            showToast("Yeni sifreler eslesmiyor.", "error");
            return { ok: false };
        }
        if (newPwd.length < 6) {
            showToast("Yeni sifre en az 6 karakter olmalidir.", "error");
            return { ok: false };
        }
        return { ok: true };
    }

    if (formEl) {
        formEl.addEventListener("submit", function (e) {
            var email = document.getElementById("email").value.trim();
            if (!email) {
                e.preventDefault();
                showToast("E-posta zorunludur.", "error");
                return;
            }
            if (!validateEmail(email)) {
                e.preventDefault();
                showToast("Gecerli bir e-posta adresi girin.", "error");
                document.getElementById("email").classList.add("is-invalid");
                return;
            }
            document.getElementById("email").classList.remove("is-invalid");

            var pwdCheck = validatePasswordChange();
            if (!pwdCheck.ok) {
                e.preventDefault();
                return;
            }
        });
    }

    function triggerPhotoInput() {
        if (photoInput) photoInput.click();
    }

    if (photoUploadBtn) {
        photoUploadBtn.addEventListener("click", triggerPhotoInput);
    }

    if (photoContainer) {
        photoContainer.addEventListener("click", function (e) {
            if (e.target.closest(".profile-photo-img") || e.target.closest(".profile-photo-placeholder")) {
                triggerPhotoInput();
            }
        });
    }

    if (photoInput) {
        photoInput.addEventListener("change", function (e) {
            var file = e.target.files[0];
            if (!file) return;

            var allowed = ["image/png", "image/jpeg", "image/jpg", "image/gif", "image/svg+xml", "image/webp"];
            if (!allowed.includes(file.type)) {
                showToast("Gecersiz dosya tipi. PNG, JPG, GIF, SVG veya WEBP secin.", "error");
                e.target.value = "";
                return;
            }
            if (file.size > 5 * 1024 * 1024) {
                showToast("Dosya boyutu maksimum 5MB olabilir.", "error");
                e.target.value = "";
                return;
            }

            var formData = new FormData();
            formData.append("file", file);
            var metaCsrf = document.querySelector('meta[name="csrf-token"]');
            if (metaCsrf && metaCsrf.getAttribute("content")) {
                formData.append("csrf_token", metaCsrf.getAttribute("content"));
            }

            var uploadUrl = profileDataEl && profileDataEl.dataset.uploadPhotoUrl ? profileDataEl.dataset.uploadPhotoUrl : "/profile/upload-photo";

            if (progressDiv) progressDiv.classList.add("visible");
            if (photoUploadBtn) photoUploadBtn.disabled = true;

            fetch(uploadUrl, {
                method: "POST",
                body: formData,
                credentials: "same-origin"
            })
                .then(function (r) { return r.json(); })
                .then(function (data) {
                    if (progressDiv) progressDiv.classList.remove("visible");
                    if (photoUploadBtn) photoUploadBtn.disabled = false;
                    if (data.success) {
                        showToast(data.message || "Fotoğraf yüklendi.", "success");
                        if (profilePictureInput) profilePictureInput.value = data.photo_url || "";

                        var placeholder = photoContainer && photoContainer.querySelector("#profilePhotoPlaceholder");
                        var existingImg = photoContainer && photoContainer.querySelector("#profilePhotoImg");
                        var photoUrl = data.photo_url || "";

                        if (placeholder) placeholder.style.display = "none";
                        if (existingImg) {
                            existingImg.src = photoUrl;
                            existingImg.style.display = "block";
                            existingImg.classList.remove("d-none");
                        } else {
                            var newImg = document.createElement("img");
                            newImg.id = "profilePhotoImg";
                            newImg.src = photoUrl;
                            newImg.alt = "Profil";
                            newImg.className = "profile-photo-img rounded-circle";
                            newImg.onclick = triggerPhotoInput;
                            if (placeholder) placeholder.remove();
                            if (photoContainer) photoContainer.insertBefore(newImg, photoContainer.firstChild);
                        }
                    } else {
                        showToast(data.message || "Yukleme hatasi.", "error");
                    }
                    e.target.value = "";
                })
                .catch(function () {
                    if (progressDiv) progressDiv.classList.remove("visible");
                    if (photoUploadBtn) photoUploadBtn.disabled = false;
                    showToast("Fotoğraf yuklenirken hata olustu.", "error");
                    e.target.value = "";
                });
        });
    }

    var profileImg = document.getElementById("profilePhotoImg");
    if (profileImg) {
        profileImg.addEventListener("click", triggerPhotoInput);
    }
})();
