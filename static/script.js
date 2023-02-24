document.addEventListener('DOMContentLoaded', activeRadio, false);
const whTooltips = { colorLinks: true, iconizeLinks: true, renameLinks: false };
var sorted = false;
function activeRadio() {
    var data = sessionStorage.getItem('data');
    if (JSON.parse(data).myRadioButtonID != '') {
        document.getElementById(JSON.parse(data).myRadioButtonID).checked = true;
    };
};
function setRadioActive(myRadio) {
    sessionStorage.setItem("data", JSON.stringify({ "myRadioButtonID": myRadio.id }));
};
function highlightRow(row) {
    var trList = document.getElementsByTagName("tr");
    for (var i = 0; i < trList.length; i++) {
        if (trList[i] != row) {
            trList[i].classList.remove("click_highlight");
        }
    };
    row.classList.toggle("click_highlight");
};
function sortTable(classColumn, elementClass, table_name) {   /* Sortiert vorerst nur Zahlen, innerHTML gibt den ganzen Zellen-Inhalt aus, deshalb musste ich noch per match den eigentlichen Wert aus 'lalala>213</span> exportieren*/
    var table, rows, switching, i, x, y, shouldSwitch;
    table = document.getElementById(table_name);
    switching = true;
    while (switching) {
        switching = false;
        rows = table.getElementsByClassName("player_row");
        for (i = 0; i < (rows.length - 1); i++) {
            shouldSwitch = false;
            x = rows[i].getElementsByClassName(elementClass)[classColumn];
            y = rows[i + 1].getElementsByClassName(elementClass)[classColumn];
            if (elementClass == "td_dungeon") {
                regex_FindNumbers = '\"([0-9]+\.*?[0-9]*?)\ ';
                if (sorted == true) {
                    if (Number(x.outerHTML.match(regex_FindNumbers)[1]) < Number(y.outerHTML.match(regex_FindNumbers)[1])) {
                        shouldSwitch = true;
                        break;
                    }
                } else {
                    if (Number(x.outerHTML.match(regex_FindNumbers)[1]) > Number(y.outerHTML.match(regex_FindNumbers)[1])) {
                        shouldSwitch = true;
                        break;
                    }
                }
            } else {
                regex_FindNumbers = '\>(\-*?[0-9]+\.*?[0-9]*?)\<';
                if (sorted == true) {
                    if (Number(x.innerHTML.match(regex_FindNumbers)[1]) < Number(y.innerHTML.match(regex_FindNumbers)[1])) {
                        shouldSwitch = true;
                        break;
                    }
                } else {
                    if (Number(x.innerHTML.match(regex_FindNumbers)[1]) > Number(y.innerHTML.match(regex_FindNumbers)[1])) {
                        shouldSwitch = true;
                        break;
                    }
                }
            }
        }
        if (shouldSwitch) {
            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
            switching = true;
        }
    }
    if (sorted == false) {
        sorted = true;
    } else {
        sorted = false
    }
};