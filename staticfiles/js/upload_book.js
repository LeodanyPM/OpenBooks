document.addEventListener("DOMContentLoaded", () => {
    const licenseType = document.getElementById("id_license_type");
    const licenseDetailGroup = document.getElementById("license-detail-group");
    const rightsDeclarationGroup = document.getElementById("rights-declaration-group");

    function updateVisibility() {
        const value = licenseType.value;
        if (value === "CC") {
            licenseDetailGroup.style.display = "block";}
        else {
            licenseDetailGroup.style.display = "none";}
        
        if (value === "OR") {
            rightsDeclarationGroup.style.display = "block";}
        else {
            rightsDeclarationGroup.style.display = "none";}}

    licenseType.addEventListener("change", updateVisibility);
    updateVisibility();
});
