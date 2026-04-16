import { createButtons } from "./buttons.js"

export function fillEventModal(data, eventosPorData, dataCompleta) {

    const divEventos = document.getElementById("eventos-lista")
    const titulo = document.getElementById("mostrarEventoModalLabel")

    divEventos.innerHTML = ""
    titulo.textContent = "Eventos do dia " + dataCompleta

    if (!eventosPorData[data]) {
        divEventos.innerHTML = "<p>Nenhum evento neste dia</p>"
        const b = document.createElement("button")
        b.classList.add("btn", "btn-primary")
        b.innerText = "Adicionar um evento a esse dia"
        b.type = "button"
        b.setAttribute("data-bs-dismiss", "modal")
        b.setAttribute("data-bs-toggle", "modal")
        b.setAttribute("data-bs-target", "#cadastrarEventoModal")
        document.getElementById("data_hora").value = data + "T00:00"
        divEventos.appendChild(b)
        return
    }

    const lista = document.createElement("ul")
    lista.classList.add("list-group")

    eventosPorData[data].forEach(evento => {
        createListItemEvent(lista, evento)
    })

    divEventos.appendChild(lista);
}


function createListItemEvent(lista, evento) {
    const li = document.createElement("li")
    li.classList.add("list-group-item")

    const container = document.createElement("div")
    container.classList.add("d-flex", "flex-column")

    // ===== Linha de cima =====
    const topRow = document.createElement("div")
    topRow.classList.add("d-flex", "justify-content-between", "align-items-center")

    const leftSide = document.createElement("div")
    leftSide.classList.add("form-check")

    const input = document.createElement("input")
    input.type = "checkbox"
    input.classList.add("form-check-input")

    const label = document.createElement("label")
    label.classList.add("form-check-label")

    if (evento.completado) {
        input.checked = true
        label.style.textDecoration = "line-through"
    }

    input.addEventListener("change", () => {
        label.style.textDecoration = input.checked ? "line-through" : "none"
        checkEvent(evento.id, evento)
    })

    const hora = evento.data_hora.split("T")[1].slice(0, 5)
    label.textContent = `${evento.titulo} às ${hora}`

    leftSide.appendChild(input)
    leftSide.appendChild(label)

    topRow.appendChild(leftSide)

    // botões continuam na direita
    createButtons(topRow, evento)

    // ===== Descrição (linha de baixo) =====
    const descricao = document.createElement("small")
    descricao.classList.add("text-muted", "ms-4")

    let descricaoCurta = evento.descricao || ""
    if (descricaoCurta.length > 50) {
        descricaoCurta = descricaoCurta.slice(0, 50) + "..."
    }

    descricao.textContent = descricaoCurta

    // ===== Montagem =====
    container.appendChild(topRow)
    container.appendChild(descricao)

    li.appendChild(container)
    lista.appendChild(li)
}


function checkEvent(eventId, evento) {
    fetch(`/checar/evento/${eventId}`, {
        method: "POST"
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Erro ao checar evento")
        }
        return response.text()
    })
    .then(() => {
        console.log("Evento marcado como completado")
    })
    .catch(error => {
        console.error(error)
    })

    evento.completado = !evento.completado
}