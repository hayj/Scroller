

function getRandomFloat()
{
    return Math.random()
}

function makeid() {
    var text = "";
    var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

    for (var i = 0; i < 5; i++)
        text += possible.charAt(Math.floor(Math.random() * possible.length));
    return text;
    }

function getTimestamp()
{
    return window.performance && window.performance.now && window.performance.timing && window.performance.timing.navigationStart ? window.performance.now() + window.performance.timing.navigationStart : Date.now();

}

function addLines(id, nbLines)
{
    for(i = 0 ; i < nbLines ; i++)
    {
        textToAdd = makeid() + makeid() + makeid() + makeid() + makeid()
        $("#" + id).append(textToAdd + "<br/>");
        if(getRandomFloat() > 0.8)
        {
            $("#" + id).append("-------------------------------------------------------------------------------------------------------------" + "<br/>");
        }
    }
}




function getDocHeight()
{
    var D = document;
    return Math.max(
        D.body.scrollHeight, D.documentElement.scrollHeight,
        D.body.offsetHeight, D.documentElement.offsetHeight,
        D.body.clientHeight, D.documentElement.clientHeight
    );
}

function getWindowSize()
{
  var myWidth = 0, myHeight = 0;
  if( typeof( window.innerWidth ) == 'number' ) {
    //Non-IE
    myWidth = window.innerWidth;
    myHeight = window.innerHeight;
  } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
    //IE 6+ in 'standards compliant mode'
    myWidth = document.documentElement.clientWidth;
    myHeight = document.documentElement.clientHeight;
  } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
    //IE 4 compatible
    myWidth = document.body.clientWidth;
    myHeight = document.body.clientHeight;
  }
  return [myWidth, myHeight];
}

function sleep (time)
{
    return new Promise(function (resolve) { setTimeout(resolve, time) });
}