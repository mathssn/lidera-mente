  
function carregarCalendario(ano, mes) {

    fetch('/calendario/' + ano + '/' + mes)
    .then(r => r.json())
    .then(data => {

        const semanas = data.semanas
        const eventos = data.eventos
        const mesNome = document.getElementById("mes_nome")
        mesNome.textContent = data.mes_nome + "/" + ano
        const tabela = document.getElementById("calendario")

        tabela.innerHTML = ""

        // mapa de eventos por data
        const eventosPorData = {}

        eventos.forEach(ev => {
            let dataEvento = ev.data_hora

            // remove hora se vier com espaço
            if (dataEvento.includes(" ")) {
                dataEvento = dataEvento.split(" ")[0]
            }

            // remove hora se vier em ISO
            if (dataEvento.includes("T")) {
                dataEvento = dataEvento.split("T")[0]
            }

            if (!eventosPorData[dataEvento]) {
                eventosPorData[dataEvento] = []
            }

            eventosPorData[dataEvento].push(ev)
        })


        // HEADER
        const thead = document.createElement("thead")
        const trHead = document.createElement("tr")

        const dias = ["Dom","Seg","Ter","Qua","Qui","Sex","Sab"]

        dias.forEach(d => {
            const th = document.createElement("th")
            th.textContent = d
            trHead.appendChild(th)
        })

        thead.appendChild(trHead)
        tabela.appendChild(thead)

        // BODY
        const tbody = document.createElement("tbody")
        semanas.forEach(semana => {

            const tr = document.createElement("tr")

            semana.forEach(dataCompleta => {
                const td = document.createElement("td")

                const [dia, mesData, anoData] = dataCompleta.split("/")

                // mostrar só o dia
                td.textContent = parseInt(dia)
                td.style.height = "100px"

                const agora = new Date();
                if (agora.getDate() == dia && agora.getMonth()+1 == mesData && agora.getFullYear() == anoData) {
                    td.style.backgroundColor = "var(--blue-100)"
                }

                // data formato ISO para comparar eventos
                const dataISO = `${anoData}-${mesData}-${dia}`

                // dias fora do mês atual
                if (parseInt(mesData) !== mes) {
                    td.style.opacity = "0.35"
                }

                // indicador de evento
                if (eventosPorData[dataISO]) {

                    const indicador = document.createElement("div")
                    indicador.style.width = "6px"
                    indicador.style.height = "6px"
                    indicador.style.background = "#2196f3"
                    indicador.style.borderRadius = "50%"
                    indicador.style.margin = "4px auto 0"

                    td.appendChild(indicador)
                }

                td.addEventListener("click", () => {
                    fillEventModal(dataISO, eventosPorData, dataCompleta)

                    const modal = new bootstrap.Modal(
                        document.getElementById("mostrarEventoModal")
                    )

                    modal.show()
                })

                tr.appendChild(td)

            })

            tbody.appendChild(tr)

        })

        tabela.appendChild(tbody)

    })
}

function fillEventModal(data, eventosPorData, dataCompleta) {

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
    input.type = "checkbox"
    input.classList.add("form-check-input")

    if (evento.completado) {
        input.checked = true
    }

    input.addEventListener("change", () => checkEvent(evento.id, evento))

    div.appendChild(input)

    const label = document.createElement("label")
    label.textContent = evento.titulo
    label.classList.add("form-check-label")

    div.appendChild(label)
    li.appendChild(div)
    createButtons(li)

    lista.appendChild(li)
}


function createButtons(li) {
    const div = document.createElement("div")
    div.classList.add('d-flex')
    div.classList.add('gap-2')

    const edButton = document.createElement("button")
    edButton.classList.add("btn", "btn-primary")

    edButton.style.width = "32px"
    edButton.style.height = "32px"
    edButton.style.display = "flex"
    edButton.style.alignItems = "center"
    edButton.style.justifyContent = "center"
    edButton.style.padding = "0" 

    const i = document.createElement("i")
    i.classList.add("bi", "bi-pencil-square")
    i.style.fontSize = "16px"

    edButton.appendChild(i)
    div.appendChild(edButton)

    const exButton = document.createElement("button")
    exButton.classList.add("btn", "btn-danger")

    exButton.style.width = "32px"
    exButton.style.height = "32px"
    exButton.style.display = "flex"
    exButton.style.alignItems = "center"
    exButton.style.justifyContent = "center"
    exButton.style.padding = "0" 

    const i2 = document.createElement("i")
    i2.classList.add("bi", "bi-trash")
    i2.style.fontSize = "16px"

    exButton.appendChild(i2)
    div.appendChild(exButton)

    li.appendChild(div)
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