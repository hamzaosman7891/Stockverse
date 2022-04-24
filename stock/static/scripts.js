function negativeNumbers() {
    var money = document.getElementsByClassName("shares");
    for (var i = 0, len = money.length; i < len; i++) {
      if (money[i].innerHTML < 0 || money[i].innerHTML.indexOf("-") > -1) {
          money[i].style.color = "red";
      }
    }
}

function calcTrans(avgprice, price, shares){
    proceeds = shares * price;
    pl = shares * price - shares * avgprice;
    document.getElementById("proceeds").innerHTML = proceeds.toLocaleString('en-US', {style: 'currency', currency: 'USD'});
    document.getElementById("pl").innerHTML = pl.toLocaleString('en-US', {style: 'currency', currency: 'USD'});
    negativeNumbers();
}

function calcCash(price, shares){
    required = price * shares;
    document.getElementById("required").innerHTML = required.toLocaleString('en-US', {style: 'currency', currency: 'USD'});
    negativeNumbers();
}


