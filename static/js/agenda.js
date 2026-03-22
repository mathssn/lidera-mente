import { fillEventModal } from "./eventModal.js"

const config = document.getElementById('calendario-config')
let ano = parseInt(config.dataset.ano)
let mes = parseInt(config.dataset.mes)

function normalizarData(dataHora) {
    return dataHora.split(/[ T]/)[0]
}

function mapearEventosPorData(eventos) {
    const mapa = {}
    eventos.forEach(ev => {
        const data = normalizarData(ev.data_hora)
        if (!mapa[data]) mapa[data] = []
        mapa[data].push(ev)
    })
    return mapa
}

function criarThead() {
    const thead = document.createElement("thead")
    const tr = document.createElement("tr")
    ;["Dom","Seg","Ter","Qua","Qui","Sex","Sab"].forEach(d => {
        const th = document.createElement("th")
        th.textContent = d
        tr.appendChild(th)
    })
    thead.appendChild(tr)
    return thead
}

function criarTarjaEvento(titulo, reticencias = false) {
    const div = document.createElement("div")
    const texto = reticencias ? "..." : (titulo.length > 10 ? titulo.slice(0, 9) + "…" : titulo)
    div.classList.add("event-tag")

    Object.assign(div.style, {
        color: "#000000",
        borderRadius: "3px",
        fontSize: "11px",
        padding: "1px 5px",
        marginTop: "3px",
        whiteSpace: "nowrap",
        overflow: "hidden",
        textOverflow: "ellipsis",
        cursor: "pointer",
    })

    div.textContent = texto
    return div
}

function ehHoje(dia, mes, ano) {
    const agora = new Date()
    return agora.getDate() == dia &&
           agora.getMonth() + 1 == mes &&
           agora.getFullYear() == ano
}

function criarTd(dataCompleta, mes, eventosPorData) {
    const [dia, mesData, anoData] = dataCompleta.split("/")
    const dataISO = `${anoData}-${mesData}-${dia}`
    const td = document.createElement("td")

    td.style.height = "100px"
    td.style.verticalAlign = "top"
    td.style.padding = "4px"

    td.addEventListener("mouseenter", () => {
        td.style.transform = "scale(1.02)"
    })

    td.addEventListener("mouseleave", () => {
        td.style.transform = "scale(1)"
    })

    // Número do dia
    const numeroDia = document.createElement("div")
    numeroDia.textContent = parseInt(dia)
    td.appendChild(numeroDia)

    if (ehHoje(dia, mesData, anoData)) {
        td.style.backgroundColor = "var(--blue-100)"
    }

    if (parseInt(mesData) !== mes) {
        td.style.opacity = "0.35"
    }

    const eventos = eventosPorData[dataISO]
    if (eventos && eventos.length > 0) {
        // Exibe as duas primeiras tarjas
        const visiveis = eventos.slice(0, 2)
        visiveis.forEach(ev => {
            td.appendChild(criarTarjaEvento(ev.titulo))
        })

        // Se houver 3 ou mais, adiciona tarja "..."
        if (eventos.length > 2) {
            td.appendChild(criarTarjaEvento(null, true))
        }
    }

    td.addEventListener("click", () => {
        fillEventModal(dataISO, eventosPorData, dataCompleta)
        new bootstrap.Modal(document.getElementById("mostrarEventoModal")).show()
    })

    return td
}

function criarTbody(semanas, mes, eventosPorData) {
    const tbody = document.createElement("tbody")
    semanas.forEach(semana => {
        const tr = document.createElement("tr")
        semana.forEach(dataCompleta => {
            tr.appendChild(criarTd(dataCompleta, mes, eventosPorData))
        })
        tbody.appendChild(tr)
    })
    return tbody
}

function carregarCalendario(ano, mes) {
    fetch(`/calendario/${ano}/${mes}`)
        .then(r => r.json())
        .then(data => {
            document.getElementById("mes_nome").textContent = `${data.mes_nome}/${ano}`

            const tabela = document.getElementById("calendario")
            tabela.innerHTML = ""

            const eventosPorData = mapearEventosPorData(data.eventos)

            tabela.appendChild(criarThead())
            tabela.appendChild(criarTbody(data.semanas, mes, eventosPorData))
        })
}

function changeCalendar(direcao) {
    mes += direcao
    if (mes < 1) { mes = 12; ano -= 1 }
    else if (mes > 12) { mes = 1; ano += 1 }
    carregarCalendario(ano, mes)
}

carregarCalendario(ano, mes)
window.changeCalendar = changeCalendar
