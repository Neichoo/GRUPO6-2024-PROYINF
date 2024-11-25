function toggleFilterSidebar() {
    const sidebar = document.getElementById('filterSidebar');
    sidebar.classList.toggle('show');
    sidebar.classList.toggle('hide');
}

function toggleFilterTags() {
    const filterDiv = document.getElementById('filter');
    const arrow = document.querySelector('.toggle-arrow i');
    if (filterDiv.style.display === 'none') {
        filterDiv.style.display = 'block';
        arrow.classList.add('expanded');
    } else {
        filterDiv.style.display = 'none';
        arrow.classList.remove('expanded');
    }
}