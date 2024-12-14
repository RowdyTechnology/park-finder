// Ensure DOM is fully loaded before running the scripts
document.addEventListener("DOMContentLoaded", () => {
    // Helper function: Get DOM element by ID
    const getElement = (id) => document.getElementById(id);

    // Dark Mode Toggle
    const darkModeToggleDesktop = getElement("darkModeToggleDesktop");
    const darkModeToggleMobile = getElement("darkModeToggleMobile");
    const themeIconDesktop = getElement("themeIconDesktop");
    const themeIconMobile = getElement("themeIcon");

    const toggleDarkMode = () => {
        document.body.classList.toggle("dark-mode");
        const isDarkMode = document.body.classList.contains("dark-mode");
        if (themeIconDesktop) themeIconDesktop.classList.toggle("bi-sun", isDarkMode);
        if (themeIconMobile) themeIconMobile.classList.toggle("bi-sun", isDarkMode);
        localStorage.setItem("theme", isDarkMode ? "dark" : "light");
    };

    // Initialize dark mode based on localStorage
    if (localStorage.getItem("theme") === "dark") {
        document.body.classList.add("dark-mode");
        if (themeIconDesktop) themeIconDesktop.classList.replace("bi-moon", "bi-sun");
        if (themeIconMobile) themeIconMobile.classList.replace("bi-moon", "bi-sun");
    }

    // Add event listeners for dark mode toggles
    if (darkModeToggleDesktop) darkModeToggleDesktop.addEventListener("click", toggleDarkMode);
    if (darkModeToggleMobile) darkModeToggleMobile.addEventListener("click", toggleDarkMode);

    // Toast Notifications
    const showToast = (message, type = "success") => {
        const toastContainer = getElement("toastContainer") || createToastContainer();
        const toast = document.createElement("div");
        toast.className = `toast align-items-center text-bg-${type} border-0`;
        toast.role = "alert";
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        toastContainer.appendChild(toast);
        new bootstrap.Toast(toast).show();
        toast.addEventListener("hidden.bs.toast", () => toast.remove());
    };

    const createToastContainer = () => {
        const container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "position-fixed bottom-0 end-0 p-3";
        container.style.zIndex = 1055;
        document.body.appendChild(container);
        return container;
    };

    // Load Parks into the Table
    const loadParks = () => {
        axios.get("/parks/")
            .then((response) => {
                const parks = response.data;
                const tableBody = getElement("parksTableBody");
                if (tableBody) {
                    tableBody.innerHTML = ""; // Clear existing rows
                    parks.forEach((park, index) => {
                        const row = `
                            <tr>
                                <td>${park.name || "Unknown"}</td>
                                <td>${park.average_rating ? park.average_rating.toFixed(2) : "N/A"}</td>
                                <td>${park.username || "Unknown"}</td>
                                <td>${park.latitude}, ${park.longitude}</td>
                                <td>${park.crowd_rating || "N/A"}</td>
                                <td>${park.obstacle_rating || "N/A"}</td>
                                <td>${park.size_rating || "N/A"}</td>
                                <td>${park.visibility_rating || "N/A"}</td>
                                <td>${park.diversity_rating || "N/A"}</td>
                                <td>${park.date_visited || "N/A"}</td>
                                <td>
                                    ${park.photo ? `<img src="${park.photo}" width="100" class="img-thumbnail" alt="Park photo" onclick="openImageModal('${park.photo}')">` : "No Photo"}
                                </td>
                                <td>
                                    <button class="btn btn-warning btn-sm" onclick="openEditModal(${index})">Edit</button>
                                    <button class="btn btn-danger btn-sm" onclick="deletePark(${index})">Delete</button>
                                </td>
                            </tr>
                        `;
                        tableBody.insertAdjacentHTML("beforeend", row);
                    });
                }
            })
            .catch(() => showToast("Failed to load parks. Please try again.", "danger"));
    };

    // Pop-Out Image Modal
    window.openImageModal = (photoUrl) => {
        const imageModal = getElement("imageModal");
        const modalImage = getElement("fullSizeImage");

        if (imageModal && modalImage) {
            modalImage.src = photoUrl;
            new bootstrap.Modal(imageModal).show();
        }
    };

    // Edit Park Functionality
    const openEditModal = (index) => {
        axios.get(`/parks/${index}`)
            .then((response) => {
                const park = response.data;
                // Populate modal fields with park data
                getElement("editName").value = park.name || "";
                getElement("editLatitude").value = park.latitude || "";
                getElement("editLongitude").value = park.longitude || "";
                getElement("editCrowdRating").value = park.crowd_rating || "";
                getElement("editObstacleRating").value = park.obstacle_rating || "";
                getElement("editSizeRating").value = park.size_rating || "";
                getElement("editVisibilityRating").value = park.visibility_rating || "";
                getElement("editDiversityRating").value = park.diversity_rating || "";
                getElement("editUsername").value = park.username || "";
                getElement("editIndex").value = index; // Hidden field for index
                new bootstrap.Modal(getElement("editModal")).show();
            })
            .catch(() => showToast("Failed to fetch park details for editing.", "danger"));
    };

    const saveEditedPark = () => {
        const index = getElement("editIndex").value;
        const editedPark = {
            name: getElement("editName").value,
            latitude: getElement("editLatitude").value,
            longitude: getElement("editLongitude").value,
            crowd_rating: getElement("editCrowdRating").value,
            obstacle_rating: getElement("editObstacleRating").value,
            size_rating: getElement("editSizeRating").value,
            visibility_rating: getElement("editVisibilityRating").value,
            diversity_rating: getElement("editDiversityRating").value,
            username: getElement("editUsername").value,
        };

        axios.put(`/parks/edit/${index}`, editedPark)
            .then(() => {
                showToast("Park updated successfully!", "success");
                loadParks(); // Reload parks
                bootstrap.Modal.getInstance(getElement("editModal")).hide();
            })
            .catch(() => showToast("Failed to update park. Please try again.", "danger"));
    };

    if (getElement("saveEditButton")){
        getElement("saveEditButton").addEventListener("click", saveEditedPark);
    }

    // Delete Park Functionality
    const deletePark = (index) => {
        if (!confirm("Are you sure you want to delete this park?")) return;

        axios.delete(`/parks/delete/${index}`)
            .then(() => {
                showToast("Park deleted successfully!", "success");
                loadParks(); // Reload parks
            })
            .catch(() => showToast("Failed to delete park. Please try again.", "danger"));
    };

    // Feature Request Form Submission
    const featureRequestForm = getElement("featureRequestForm");
    if (featureRequestForm) {
        featureRequestForm.addEventListener("submit", (e) => {
            e.preventDefault(); // Prevent default form submission

            const title = getElement("requestTitle").value.trim();
            const description = getElement("requestDescription").value.trim();
            const priority = getElement("requestPriority").value;

            if (!title || !description || !priority) {
                showToast("Please fill out all fields before submitting.", "warning");
                return;
            }

            const requestData = {
                title: title,
                description: description,
                priority: priority,
            };

            axios.post("/feature_requests/submit", requestData)
                .then(() => {
                    showToast("Feature request submitted successfully!", "success");
                    featureRequestForm.reset();
                })
                .catch(() => showToast("Failed to submit feature request. Please try again.", "danger"));
        });
    }

    // Export Parks to KML
    const exportToKMLButton = getElement("exportToKML");
    if (exportToKMLButton) {
        exportToKMLButton.addEventListener("click", () => {
            axios.get("/parks/")
                .then((response) => {
                    const parks = response.data;
                    const kml = `<?xml version="1.0" encoding="UTF-8"?>
                        <kml xmlns="http://www.opengis.net/kml/2.2">
                        <Document>
                        ${parks.map((park) => `
                            <Placemark>
                                <name>${park.name}</name>
                                <Point>
                                    <coordinates>${park.longitude},${park.latitude},0</coordinates>
                                </Point>
                            </Placemark>`).join("")}
                        </Document>
                        </kml>`;
                    const blob = new Blob([kml], { type: "application/vnd.google-earth.kml+xml" });
                    const link = document.createElement("a");
                    link.href = URL.createObjectURL(blob);
                    link.download = "parks.kml";
                    link.click();
                    showToast("Parks exported to KML successfully!", "success");
                })
                .catch(() => showToast("Failed to export parks to KML.", "danger"));
        });
    }

    // Load Feature Requests
    const loadFeatureRequests = () => {
        axios.get("/feature_requests/")
            .then((response) => {
                const requests = response.data;
                const tableBody = getElement("featureRequestsTableBody");
                if (tableBody) {
                    tableBody.innerHTML = "";
                    requests.forEach((request) => {
                        const row = `
                            <tr>
                                <td>${request.title || "N/A"}</td>
                                <td>${request.description || "N/A"}</td>
                                <td>${request.priority || "N/A"}</td>
                                <td>${request.date_submitted || "N/A"}</td>
                            </tr>
                        `;
                        tableBody.insertAdjacentHTML("beforeend", row);
                    });
                }
            })
            .catch(() => showToast("Failed to load feature requests.", "danger"));
    };

    // Sort Table Function
    window.sortTable = (columnIndex) => {
        const table = document.getElementById("parksTable");
        const tbody = table.querySelector("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr"));
        const header = table.querySelectorAll("th")[columnIndex];
        const sortOrder = header.getAttribute("data-sort-order") === "asc" ? "desc" : "asc";

        rows.sort((rowA, rowB) => {
            const cellA = rowA.querySelectorAll("td")[columnIndex].textContent.trim();
            const cellB = rowB.querySelectorAll("td")[columnIndex].textContent.trim();

            if (sortOrder === "asc") {
                return cellA.localeCompare(cellB, undefined, { numeric: true });
            } else {
                return cellB.localeCompare(cellA, undefined, { numeric: true });
            }
        });

        tbody.innerHTML = "";
        rows.forEach(row => tbody.appendChild(row));

        // Update sort order attribute
        table.querySelectorAll("th").forEach(th => th.removeAttribute("data-sort-order"));
        header.setAttribute("data-sort-order", sortOrder);
    };

    // Sort Table Function for Feature Requests
    window.sortTableFeatureRequests = (columnIndex) => {
        const table = document.getElementById("featureRequestsTable");
        const tbody = table.querySelector("tbody");
        const rows = Array.from(tbody.querySelectorAll("tr"));
        const header = table.querySelectorAll("th")[columnIndex];
        const sortOrder = header.getAttribute("data-sort-order") === "asc" ? "desc" : "asc";

        rows.sort((rowA, rowB) => {
            const cellA = rowA.querySelectorAll("td")[columnIndex].textContent.trim();
            const cellB = rowB.querySelectorAll("td")[columnIndex].textContent.trim();

            if (sortOrder === "asc") {
                return cellA.localeCompare(cellB, undefined, { numeric: true });
            } else {
                return cellB.localeCompare(cellA, undefined, { numeric: true });
            }
        });

        tbody.innerHTML = "";
        rows.forEach(row => tbody.appendChild(row));

        // Update sort order attribute
        table.querySelectorAll("th").forEach(th => th.removeAttribute("data-sort-order"));
        header.setAttribute("data-sort-order", sortOrder);
    };

    // Home Point Form
    const homePointForm = getElement("homePointForm");
    if (homePointForm) {
        homePointForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const latitude = getElement("homeLatitude").value;
            const longitude = getElement("homeLongitude").value;

            axios.post("/parks/home_point", { latitude, longitude })
                .then(() => {
                    showToast("Home point set successfully!", "success");
                })
                .catch(() => showToast("Failed to set home point.", "danger"));
        });
    }

    // Get Current Location
    const getLocationButton = getElement("getLocation");
    const latitudeInput = getElement("latitude");
    const longitudeInput = getElement("longitude");

    if (getLocationButton && latitudeInput && longitudeInput) {
        getLocationButton.addEventListener("click", () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        latitudeInput.value = position.coords.latitude;
                        longitudeInput.value = position.coords.longitude;
                    },
                    () => {
                        showToast("Geolocation is not supported by this browser.", "warning");
                    }
                );
            } else {
                showToast("Geolocation is not supported by this browser.", "warning");
            }
        });
    }

    // Get Current Location for Home Point
    const getHomeLocationButton = getElement("getHomeLocation");
    const homeLatitudeInput = getElement("homeLatitude");
    const homeLongitudeInput = getElement("homeLongitude");

    if (getHomeLocationButton && homeLatitudeInput && homeLongitudeInput) {
        getHomeLocationButton.addEventListener("click", () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        homeLatitudeInput.value = position.coords.latitude;
                        homeLongitudeInput.value = position.coords.longitude;
                    },
                    () => {
                        showToast("Geolocation is not supported by this browser.", "warning");
                    }
                );
            } else {
                showToast("Geolocation is not supported by this browser.", "warning");
            }
        });
    }

    // Date and Time Input
    const setDateTimeButton = getElement("setDateTime");
    const dateVisitedInput = getElement("dateVisited");

    if (setDateTimeButton && dateVisitedInput) {
        setDateTimeButton.addEventListener("click", () => {
            const now = new Date();
            const formattedDateTime = now.toLocaleString('en-US', {
                timeZoneName: 'short', // Show timezone abbreviation
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
            });
            dateVisitedInput.value = formattedDateTime;
        });
    }

    // Add Park Form Submission
    const addParkForm = getElement("addParkForm");
    if (addParkForm) {
        addParkForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const formData = new FormData(addParkForm);

            axios.post("/add_park", formData)
                .then(() => {
                    showToast("Park added successfully!", "success");
                    addParkForm.reset();
                })
                .catch(() => showToast("Failed to add park.", "danger"));
        });
    }

    // Initialize
    loadParks();
    if (window.location.pathname === "/view_feature_requests") {
        loadFeatureRequests();
    }
});