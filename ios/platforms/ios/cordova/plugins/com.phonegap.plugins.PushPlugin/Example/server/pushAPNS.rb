require 'rubygems'
require 'pushmeup'


APNS.host = 'gateway.sandbox.push.apple.com'
APNS.port = 2195
APNS.pem  = '/Users/weel/Desktop/ck.pem'
APNS.pass = 'pale360#ward'

raise "The path to your pem file does not exist!" unless File.exist?(APNS.pem)

device_token = '8286ce54933d2eadacf50c093b20b8b193d6a86f07c57a087abc28214c779afc'
# APNS.send_notification(device_token, 'Hello iPhone!' )
APNS.send_notification(device_token, :alert => 'PushPlugin works!!', :badge => 1, :sound => 'beep.wav')
