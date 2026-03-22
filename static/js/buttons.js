function createIcon(iconClass) {
    const i = document.createElement("i")
    i.classList.add("bi", iconClass)
    i.style.fontSize = "16px"
    return i
}

function createIconButton(btnClass, iconClass, evento) {
    const button = document.createElement("button")
    button.classList.add("btn", btnClass)
    Object.assign(button.style, {
        width: "32px",
        height: "32px",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "0"
    })

    button.appendChild(createIcon(iconClass))

    if (iconClass == "bi-pencil-square") {
        button.type = "button"
        button.setAttribute("data-bs-dismiss", "modal")
        button.setAttribute("data-bs-toggle", "modal")
        button.setAttribute("data-bs-target", "#editEventoModal")

        button.addEventListener("click", () => {
            document.getElementById('edit_titulo').value = evento.titulo
            document.getElementById('edit_descricao').value = evento.descricao
            document.getElementById('edit_data_hora').value = evento.data_hora
    
            document.getElementById("editEventoForm").action = "/editar/evento/0".replace('0', evento.id);
        })
    } else if (iconClass == "bi-trash") {
        button.type = "submit"
        const form = document.createElement("form")
        form.action = "/excluir/evento/0".replace('0', evento.id)
        form.method = "POST"
        form.addEventListener("submit", () => {
            return confirm('Tem certeza que deseja excluir este item?')
        })

        form.appendChild(button)
        return form
    }

    return button
}

export function createButtons(li, evento) {
    const div = document.createElement("div")
    div.classList.add("d-flex", "gap-2")

    div.appendChild(createIconButton("btn-primary", "bi-pencil-square", evento))
    div.appendChild(createIconButton("btn-danger", "bi-trash", evento))

    li.appendChild(div)
}
