  
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

    const list = document.getElementById("eventos-lista")
    const titulo = document.getElementById("mostrarEventoModalLabel")

    list.innerHTML = ""
    titulo.textContent = "Eventos do dia " + dataCompleta

    if (!eventosPorData[data]) {
        list.innerHTML = "<p>Nenhum evento neste dia</p>"
        return
    }

    eventosPorData[data].forEach(evento => {

        const div = document.createElement("div")
        div.classList.add("form-check")

        const input = document.createElement("input")
        input.type = "checkbox"
        input.classList.add("form-check-input")

        if (evento.completado) {
            input.checked = true
        }

        input.addEventListener("change", () => checkEvent(evento.id))

        div.appendChild(input)

        const label = document.createElement("label")
        label.textContent = evento.titulo
        label.classList.add("form-check-label")

        div.appendChild(label)

        list.appendChild(div)

    })
}

function checkEvent(eventId) {
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
}