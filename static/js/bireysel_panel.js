document.addEventListener('DOMContentLoaded', function () {
    const todo = document.getElementById('todo-column');
    const inprogress = document.getElementById('inprogress-column');
    const done = document.getElementById('done-column');

    if (!todo || !inprogress || !done) return;

    const emptyCard = (text) => `
        <div class="task-card p-3 mb-2 border rounded bg-white text-muted">
            ${text}
        </div>
    `;

    todo.insertAdjacentHTML('beforeend', emptyCard('Yapılacak görev yok.'));
    inprogress.insertAdjacentHTML('beforeend', emptyCard('Devam eden görev yok.'));
    done.insertAdjacentHTML('beforeend', emptyCard('Tamamlanan görev yok.'));
});
