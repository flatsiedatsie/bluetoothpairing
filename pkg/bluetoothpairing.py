"""Bluetoothpairing API handler."""



import os
import sys
import json
import time
from time import sleep
import logging
import pexpect
import pexpect.exceptions
import requests
import threading
import subprocess




try:
    from gateway_addon import APIHandler, APIResponse, Adapter, Device, Property, Database
    #print("succesfully loaded APIHandler and APIResponse from gateway_addon")
except:
    print("Import APIHandler and APIResponse from gateway_addon failed. Use at least WebThings Gateway version 0.10")
    sys.exit(1)



class BluetoothpairingAPIHandler(APIHandler):
    """Bluetoothpairing API handler."""

    def __init__(self, verbose=False):
        """Initialize the object."""
        #print("INSIDE API HANDLER INIT")
        
        
        self.addon_name = 'bluetoothpairing'
        self.running = True

        self.server = 'http://127.0.0.1:8080'
        self.DEBUG = False
            
        self.things = [] # Holds all the things, updated via the API. Used to display a nicer thing name instead of the technical internal ID.
        self.data_types_lookup_table = {}
        self.token = None
        
        self.bl = None
        
        # LOAD CONFIG
        try:
            self.add_from_config()
        except Exception as ex:
            print("Error loading config: " + str(ex))
        
        self.DEBUG = True

        first_run = False
        try:
            with open(self.persistence_file_path) as f:
                self.persistent_data = json.load(f)
                if self.DEBUG:
                    print("Persistence data was loaded succesfully.")
                
        except:
            first_run = True
            print("Could not load persistent data (if you just installed the add-on then this is normal)")
            self.persistent_data = {'items':[]}
            
        if self.DEBUG:
            print("Bluetoothpairing self.persistent_data is now: " + str(self.persistent_data))


        #try:
            #self.adapter = BluetoothpairingAdapter(self,verbose=False)
            #self.manager_proxy.add_api_handler(self.extension)
            #print("ADAPTER created")
        #except Exception as e:
        #    print("Failed to start ADAPTER. Error: " + str(e))
        
        
        
        
        # Is there user profile data?    
        #try:
        #    print(str(self.user_profile))
        #except:
        #    print("no user profile data")
                

            
            
        # Intiate extension addon API handler
        try:
            manifest_fname = os.path.join(
                os.path.dirname(__file__),
                '..',
                'manifest.json'
            )

            with open(manifest_fname, 'rt') as f:
                manifest = json.load(f)

            APIHandler.__init__(self, manifest['id'])
            self.manager_proxy.add_api_handler(self)
            

            if self.DEBUG:
                print("self.manager_proxy = " + str(self.manager_proxy))
                print("Created new API HANDLER: " + str(manifest['id']))
        
        except Exception as e:
            print("Failed to init UX extension API handler: " + str(e))

        

        # Respond to gateway version
        try:
            if self.DEBUG:
                print("Mozilla Gateway version: " + str(self.gateway_version))
        except:
            print("self.gateway_version did not exist")

        # Start the internal clock
        #print("Starting the internal clock")
        #try:            
        #    t = threading.Thread(target=self.clock)
        #    t.daemon = True
        #    t.start()
        #except:
        #    print("Error starting the clock thread")
        
        print("bl")
        try:
            self.bl = Bluetoothctl()
            self.bl.make_agent()
            

            
            if self.DEBUG:
                print("bluetooth seems ok: " + str(self.gateway_version))
        except Exception as ex:
            print("Error initialising bluetooth object: " + str(ex))




    # Read the settings from the add-on settings page
    def add_from_config(self):
        """Attempt to read config data."""
        try:
            database = Database(self.addon_name)
            if not database.open():
                print("Could not open settings database")
                return
            
            config = database.load_config()
            database.close()
            
        except:
            print("Error! Failed to open settings database.")
        
        if not config:
            print("Error loading config from database")
            return
        
        

        if 'Debugging' in config:
            self.DEBUG = bool(config['Debugging'])
            if self.DEBUG:
                print("-Debugging preference was in config: " + str(self.DEBUG))




#
#  HANDLE REQUEST
#

    def handle_request(self, request):
        """
        Handle a new API request for this handler.

        request -- APIRequest object
        """
        
        try:
        
            if request.method != 'POST':
                return APIResponse(status=404)
            
            if request.path == '/init' or request.path == '/update' or request.path == '/scan' or request.path == '/exit':

                try:
                    
                    if request.path == '/init':
                        if self.DEBUG:
                            print("/init - Getting the initialisation data")
                            
                        try:
                            state = 'ok'

                            #print("making bluetooth discoverable")
                            #self.bl.make_discoverable()
                            
                            #self.bl.start_scan()
                            #sleep(1)
                            
                            #print(str( self.bl.get_available_controllers() ))
            
                            
                            #self.bl.make_pairable()
                            self.bl.make_discoverable()
                            
                            
            
                            self.bl.start_scan()
                            
                            #self.available_devices = self.bl.get_available_devices()
                            #print(str(self.available_devices))
                            
                            #self.bl.stop_scan()
                            
                            
                            #self.bl.start_scan()
            
                            sleep(3)
                            self.bl.stop_scan()

                            paired_devices = self.bl.get_paired_devices()
                            
                            if self.DEBUG:
                                print("raw paired devices:")
                                print(str(paired_devices))
                            
                            for i in range(len(paired_devices)):
                                paired_devices[i]['paired'] = True
                                paired_devices[i]['trusted'] = False
                                paired_devices[i]['connected'] = False
                                
                                try:
                                    mac = paired_devices[i]['mac']
                                    #print("getting extra info for paired device: " + str(mac))
                                    info_test = [] #self.bl.get_device_info(mac) # disabled, as it caused issues.
                                    #print(str(info_test))
                                    trusted = False
                                    connected = False
                                    for line in info_test:
                                        print(str(line))
                                        if 'Trusted: yes' in line:
                                            print("it was already trusted")
                                            paired_devices[i]['trusted'] = True
                                        if 'Connected: yes' in line:
                                            print("it was already connected")
                                            paired_devices[i]['connected'] = True
                                except Exception as ex:
                                    print("error doing extra test if connected: " + str(ex))
                            
                            if self.DEBUG:
                                print("Init paired:")
                                print(str(paired_devices))
                            
                            

                            return APIResponse(
                                status=200,
                                content_type='application/json',
                                content=json.dumps({'state' : state, 'items' : paired_devices}),
                            )
                        except Exception as ex:
                            print("Error getting init data: " + str(ex))
                            return APIResponse(
                                status=500,
                                content_type='application/json',
                                content=json.dumps({'state' : "Initialisation error", 'items' : []}),
                            )
                            
                            
                            
                    elif request.path == '/scan':
                        if self.DEBUG:
                            print("/scan - Scanning for bluetooth devices")
                            
                        try:
                            state = 'ok'
                            
                            #self.bl = Bluetoothctl()
                            #self.bl.make_agent()
                            
                            #self.bl.make_discoverable()
                            #self.bl.make_pairable()
                            
            
                            #self.bl.start_scan()
                            
                            #sleep(5)
                            #self.bl.stop_scan()
                            
                            #self.available_devices = self.bl.get_available_devices()
                            #print(str(self.available_devices))
                            
                            
                            all_devices = []
                            
                            paired_devices = self.bl.get_paired_devices()
                            
                            if self.DEBUG:
                                print("raw paired devices:")
                                print(str(paired_devices))
                            
                            
                            for i in range(len(paired_devices)):
                                paired_devices[i]['paired'] = True
                                paired_devices[i]['trusted'] = False
                                paired_devices[i]['connected'] = False
                                
                                
                                try:
                                    mac = paired_devices[i]['mac']
                                    #print("getting extra info for paired device: " + str(mac))
                                    info_test = [] # getting device info was causing issues
                                    #info_test = self.bl.get_device_info(mac)
                                    #print(str(info_test))
                                    trusted = False
                                    connected = False
                                    for line in info_test:
                                        print(str(line))
                                        if 'Trusted: yes' in line:
                                            print("it was already trusted")
                                            paired_devices[i]['trusted'] = True
                                        if 'Connected: yes' in line:
                                            print("it was already connected")
                                            paired_devices[i]['connected'] = True
                                except Exception as ex:
                                    print("error doing extra test if connected: " + str(ex))
                                
                                all_devices.append(paired_devices[i])
                                
                                
                            discovered_devices = self.bl.get_discoverable_devices()
                            
                            if self.DEBUG:
                                print("raw discovered devices:")
                                print(str(discovered_devices))
                            
                            for i in range(len(discovered_devices)):
                                discovered_devices[i]['paired'] = False
                                discovered_devices[i]['trusted'] = False
                                discovered_devices[i]['connected'] = False
                                all_devices.append(discovered_devices[i])
                            
                            #self.bl.stop_scan()

                            return APIResponse(
                                status=200,
                                content_type='application/json',
                                content=json.dumps({'state' : state, 'items' : all_devices }),
                            )
                        except Exception as ex:
                            print("Error during scan: " + str(ex))
                            return APIResponse(
                                status=500,
                                content_type='application/json',
                                content=json.dumps({'state' : "Error while doing scan", 'items' : []}),
                            )
                            
                            
                            
                            
                            
                    elif request.path == '/update':
                        if self.DEBUG:
                            print("/update - Updating a single device")
                            
                            
                        
                            #get_device_info
                    
                        try:
                            state = 'ok'
                            action = str(request.body['action'])
                            mac = str(request.body['mac'])
                            update = "" 
                            
                            print(str(action))
                            
                            if action == 'info':
                                if self.DEBUG:
                                    print("getting info")
                                update = 'Unable to get detailed information'
                                try:
                                    update = self.bl.get_device_info(mac)
                                    #sleep(2)
                                except Exception as ex:
                                    print("error getting device info: " + str(ex))
                                    state = False
                                
                            elif action == 'pair':
                                if self.DEBUG:
                                    print("pairing...")
                                update = ''
                                try:
                                    #update = self.bl.trust(mac)
                                    #print(str(update))
                                    state = self.bl.pair(mac)
                                    #sleep(2)
                                    #print("pair succes?____")
                                    #print(str(state))
                                    #print("---------")
                                    #sleep(2)
                                    if state:
                                        update = 'paired succesfully'
                                        state = self.bl.trust(mac)
                                        #print("trust success?_____")
                                        #print(str(state))
                                        #print("---------")
                                        #sleep(2)
                                        if state:
                                            update = 'paired and connected succesfully'
                                            state2 = self.bl.connect(mac)
                                            #print("connect success?")
                                            #print(str(state2))
                                            if state2:
                                                update = 'paired, connected and trusted succesfully'
                                            else:
                                                update = 'paired, connected succesfully, but was unable to setup automatic reconnecting'
                                except Exception as ex:
                                    print("error pairing: " + str(ex))
                                    state = False
                            
                            
                            elif action == 'connect':
                                if self.DEBUG:
                                    print("connecting...")
                                update = ''
                                try:
                                    state = self.bl.trust(mac)
                                    if state:
                                        if self.DEBUG:
                                            print("Succesfully trusted device")
                                        state = self.bl.connect(mac)
                                        #sleep(2)
                                        if self.DEBUG:
                                            print("connect succes?____")
                                            print(str(state))
                                            print("---------")
                                    
                                        try:
                                            info_test = self.bl.get_device_info(mac)
                                            #print(str(info_test))
                                            for line in info_test:
                                                if self.DEBUG:
                                                    print(str(line))
                                                if 'Connected: yes' in line:
                                                    if self.DEBUG:
                                                        print("it was already connected")
                                                    state = True
                                        except Exception as ex:
                                            print("error doing extra test if connected: " + str(ex))
                                        
                                        #sleep(2)
                                        if state:
                                            update = 'connected succesfully'
                                except Exception as ex:
                                    print("error in connecting: " + str(ex))
                                    state = False
                                
                            elif action == 'unpair':
                                if self.DEBUG:
                                    print("unpairing...")
                                update = 'Unable to unpair'
                                try:
                                    state = self.bl.remove(mac)
                                    if self.DEBUG:
                                        print("remove success?______")
                                        print(str(state))
                                        print("---------")
                                    #sleep(2)
                                except Exception as ex:
                                    print("error in pairing: " + str(ex))
                                    state = False
                                

                            return APIResponse(
                                status=200,
                                content_type='application/json',
                                content=json.dumps({'state' : state, 'mac': mac,'update' : update }),
                            )
                        except Exception as ex:
                            print("Error updating: " + str(ex))
                            return APIResponse(
                                status=500,
                                content_type='application/json',
                                content=json.dumps({'state' : "Error while updating device", 'update' : "Server error"}),
                            )
                            
                            
                            
                            
                            
                            
                            
                            
                            
                            
                    
                    elif request.path == '/exit':
                        try:
                            if self.DEBUG:
                                print("/exit called")
                            #self.bl.stop_scan()
                            self.bl.make_pairable(False)
                            self.bl.make_discoverable(False)
                            
                            self.bl.exit()
                            
                            return APIResponse(
                                status=200,
                                content_type='application/json',
                                content=json.dumps({'state' : 'ok'}),
                            )
                        except Exception as ex:
                            print("Error updating items: " + str(ex))
                            return APIResponse(
                                status=500,
                                content_type='application/json',
                                content=json.dumps("Error updating: " + str(ex)),
                            )
                        
                    else:
                        return APIResponse(
                            status=500,
                            content_type='application/json',
                            content=json.dumps("Invalid path"),
                        )
                        
                        
                except Exception as ex:
                    print("API handler issue: " + str(ex))
                    return APIResponse(
                        status=500,
                        content_type='application/json',
                        content=json.dumps("Valid path, but general error in API handler"),
                    )
                    
            else:
                return APIResponse(status=404)
                
        except Exception as e:
            print("Failed to handle UX extension API request: " + str(e))
            return APIResponse(
                status=500,
                content_type='application/json',
                content=json.dumps("API Error"),
            )



        
#
#  Bluetooth class


# from Github user castis
# Based on ReachView code from Egor Fedorov (egor.fedorov@emlid.com)
# Updated for Python 3.6.8 on a Raspberry  Pi



class Bluetoothctl:
    """A wrapper for bluetoothctl utility."""

    def __init__(self):
        subprocess.check_output("rfkill unblock bluetooth", shell=True)
        self.process = pexpect.spawnu("sudo bluetoothctl", echo=False)

        self.logger = logging.getLogger("btctl")

    #def exit(self):
    #    try:
    #        self.process.send(f"exit\n")
    #        self.process.close(force=True)
    #    except Exception as ex:
    #        print(str(ex))
            
    def send(self, command, pause=0):
        self.process.send(f"{command}\n")
        time.sleep(pause)
        if self.process.expect(["bluetooth", pexpect.EOF]):
            raise Exception(f"failed after {command}")

    def get_output(self, *args, **kwargs):
        """Run a command in bluetoothctl prompt, return output as a list of lines."""
        self.send(*args, **kwargs)
        return self.process.before.split("\r\n")

    def start_scan(self):
        """Start bluetooth scanning process."""
        try:
            self.send("scan on")
        except Exception as e:
            self.logger.error(e)

    def stop_scan(self):
        """Stop bluetooth scanning process."""
        try:
            self.send("scan off")
        except Exception as e:
            self.logger.error(e)

    def make_discoverable(self,state=True):
        """Make device discoverable."""
        try:
            if state:
                #print("-making discoverable")
                self.send("discoverable on")
            else:
                #print("-making undiscoverable")
                self.send("discoverable off")
        except Exception as e:
            self.logger.error(e)


    def make_pairable(self,state=True):
        """Make device pairable."""
        try:
            if state:
                #print("-making pariable")
                self.send("pairable on")
            else:
                #print("-making unpariable")
                self.send("pairable off")
        except Exception as e:
            self.logger.error(e)
            
    def make_agent(self):
        """Make agent on."""
        try:
            self.send("agent on") # was agent on
            #self.send("default-agent")
            
        except Exception as e:
            self.logger.error(e)
            


    def parse_device_info(self, info_string):
        """Parse a string corresponding to a device."""
        device = {}
        block_list = ["[\x1b[0;", "removed"]
        if not any(keyword in info_string for keyword in block_list):
            try:
                device_position = info_string.index("Device")
            except ValueError:
                pass
            else:
                if device_position > -1:
                    attribute_list = info_string[device_position:].split(" ", 2)
                    device = {
                        "mac": attribute_list[1],
                        "name": attribute_list[2],
                    }
        return device

    def parse_controller_info(self, info_string):
        """Parse a string corresponding to a controller."""
        return info_string

    def get_available_controllers(self):
        """Return a list of tuples of bluetooth controllers."""
        available_controllers = []
        try:
            out = self.get_output("list")
        except Exception as e:
            self.logger.error(e)
        else:
            for line in out:
                controller = self.parse_controller_info(line)
                if controller:
                    available_controllers.append(controller)
        return available_controllers

    def get_available_devices(self):
        """Return a list of tuples of paired and discoverable devices."""
        available_devices = []
        try:
            out = self.get_output("devices")
        except Exception as e:
            self.logger.error(e)
        else:
            for line in out:
                device = self.parse_device_info(line)
                if device:
                    available_devices.append(device)
        return available_devices

    def get_paired_devices(self):
        """Return a list of tuples of paired devices."""
        paired_devices = []
        try:
            out = self.get_output("paired-devices")
        except Exception as e:
            self.logger.error(e)
        else:
            for line in out:
                print("paaaiiirrreeed??: " + str(line))
                device = self.parse_device_info(line)
                if device:
                    paired_devices.append(device)
        return paired_devices

    def get_discoverable_devices(self):
        """Filter paired devices out of available."""
        available = self.get_available_devices()
        paired = self.get_paired_devices()
        return [d for d in available if d not in paired]

    def get_device_info(self, mac_address):
        """Get device info by mac address."""
        try:
            out = self.get_output(f"info {mac_address}")
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            return out

    def pair(self, mac_address):
        """Try to pair with a device by mac address."""
        try:
            self.send(f"pair {mac_address}", 4)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to pair", "Pairing successful", pexpect.EOF]
            )
            return res == 1

    def trust(self, mac_address):
        try:
            self.send(f"trust {mac_address}", 4)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to trust", "Pairing successful", pexpect.EOF]
            )
            return res == 1

    def remove(self, mac_address):
        """Remove paired device by mac address, return success of the operation."""
        try:
            self.send(f"remove {mac_address}", 3)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["not available", "Device has been removed", pexpect.EOF]
            )
            return res == 1

    def connect(self, mac_address):
        """Try to connect to a device by mac address."""
        try:
            self.send(f"connect {mac_address}", 2)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to connect", "Connection successful", pexpect.EOF]
            )
            return res == 1

    def disconnect(self, mac_address):
        """Try to disconnect to a device by mac address."""
        try:
            self.send(f"disconnect {mac_address}", 2)
        except Exception as e:
            self.logger.error(e)
            return False
        else:
            res = self.process.expect(
                ["Failed to disconnect", "Successful disconnected", pexpect.EOF]
            )
            return res == 1

        
        
def run_command(cmd, timeout_seconds=60):
    try:
        
        p = subprocess.run(cmd, timeout=timeout_seconds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True)

        if p.returncode == 0:
            return p.stdout  + '\n' + "Command success" #.decode('utf-8')
            #yield("Command success")
        else:
            if p.stderr:
                return "Error: " + str(p.stderr)  + '\n' + "Command failed"   #.decode('utf-8'))

    except Exception as e:
        print("Error running command: "  + str(e))
        
        
def valid_mac(mac):
    return mac.count(':') == 5 and \
        all(0 <= int(num, 16) < 256 for num in mac.rstrip().split(':')) and \
        not all(int(num, 16) == 255 for num in mac.rstrip().split(':'))
