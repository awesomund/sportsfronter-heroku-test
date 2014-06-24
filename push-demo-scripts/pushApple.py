import socket, ssl, json, struct

# device token returned when the iPhone application
# registers to receive alerts

# This is test device
# For local testing you could change this to your own deviceToken
deviceToken = '525efe2ac7b851950a63dcd584d85d2eac65e522ba07f7d0375b1563e35a63cc'

# Payload limited to 256 bytes
thePayLoad = {
            'aps': {
                'alert': "Test push message",
                'sound': 'k1DiveAlarm.caf',
                'badge': 1,
            },
            'eventurl': 'AN EVENT URL WITH HASH',
        }

# Certificate issued by apple and converted to .pem format with openSSL
# Per Apple's Push Notification Guide (end of chapter 3), first export the cert in p12 format
# openssl pkcs12 -in cert.p12 -out cert.pem -nodes
#   when prompted "Enter Import Password:" hit return
#
theCertfile = 'apple_dist_key.pem'
#
# gateway.sandbox.push.apple.com for staging, need the dev certificate for that
theHost = ( 'gateway.push.apple.com', 2195 )

#
data = json.dumps( thePayLoad )

# Clear out spaces in the device token and convert to hex
deviceToken = deviceToken.replace(' ','')
#byteToken = bytes.fromhex(deviceToken) # Python 3
byteToken = deviceToken.decode('hex') # Python 2

theFormat = '!BH32sH%ds' % len(data)
theNotification = struct.pack( theFormat, 0, 32, byteToken, len(data), data )

# Create our connection using the certfile saved locally
ssl_sock = ssl.wrap_socket( socket.socket( socket.AF_INET, socket.SOCK_STREAM ), certfile = theCertfile )
ssl_sock.connect( theHost )

# Write out our data
ssl_sock.write( theNotification )

# Close the connection -- apple would prefer that we keep
# a connection open and push data as needed.
ssl_sock.close()
