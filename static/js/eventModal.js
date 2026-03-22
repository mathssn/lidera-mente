import { createButtons } from "./buttons.js"

export function fillEventModal(data, eventosPorData, dataCompleta) {

    const divEventos = document.getElementById("eventos-lista")
    const titulo = document.getElementById("mostrarEventoModalLabel")

    divEventos.innerHTML = ""
    titulo.textContent = "Eventos do dia " + dataCompleta

    if (!eventosPorData[data]) {
        divEventos.innerHTML = "<p>Nenhum evento neste dia</p>"
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
    li.classList.add("d-flex")
    li.classList.add("justify-content-between")
    li.classList.add("align-items-center")

    const div = document.createElement("div")
    div.classList.add("form-check")

    const input = document.createElement("input")
    const label = document.createElement("label")
    input.type = "checkbox"
    input.classList.add("form-check-input")

    if (evento.completado) {
        input.checked = true
        label.style.textDecoration = "line-through"
    }

    input.addEventListener("change", () => {
        label.style.textDecoration = input.checked ? "line-through" : "none"
        checkEvent(evento.id, evento)
    })

    div.appendChild(input)

    label.textContent = evento.titulo + " as " + evento.data_hora.split("T")[1].slice(0, 5)
    label.classList.add("form-check-label")

    div.appendChild(label)
    li.appendChild(div)
    createButtons(li, evento)

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