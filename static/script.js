document.addEventListener('DOMContentLoaded', activeRadio, false);
const whTooltips = { colorLinks: true, iconizeLinks: true, renameLinks: false };
var sortOrder = 'asc';
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

const sortTable = (columnIndex, elementClass, tableName) => {
  const table = document.getElementById(tableName);
  let shouldSort = true;
  
  while (shouldSort) {
    shouldSort = false;
    const rows = table.getElementsByClassName('player_row');
    for (let i = 0; i < rows.length - 1; i++) {
      var x = rows[i].getElementsByClassName(elementClass)[columnIndex];;
      var y = rows[i + 1].getElementsByClassName(elementClass)[columnIndex];;
      var currentValue = getValue(x);
      var nextValue = getValue(y);

      if (sortOrder === 'asc' ? currentValue > nextValue : currentValue < nextValue) {
        rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
        shouldSort = true;
        break;
      }
    }
  }
  sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
  
  function getValue(cell) {
    if (elementClass === 'td_dungeon') {
        return parseFloat(cell.outerHTML.match('\"([0-9]+\.*?[0-9]*?)\ ')[1]);
    } else if (elementClass === 'td_player') {
        return cell.querySelector('p').textContent;
    } else if (elementClass === 'td_achiev') {
        return parseInt(cell.textContent,10);
    } else {
      return parseFloat(cell.innerHTML.match('\>(\-*?[0-9]+\.*?[0-9]*?)\<')[1]);
    }
  }
};