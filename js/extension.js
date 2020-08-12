(function() {
    class Bluetoothpairing extends window.Extension {
        constructor() {
            super('bluetoothpairing');
            //console.log("Adding bluetoothpairing addon to menu");
            this.addMenuEntry('Bluetoothpairing');

            this.content = '';

            this.item_elements = ['name', 'mac'];
            this.all_things;
            this.items_list = [];

            this.item_number = 0;

            fetch(`/extensions/${this.id}/views/content.html`)
                .then((res) => res.text())
                .then((text) => {
                    this.content = text;
                })
                .catch((e) => console.error('Failed to fetch content:', e));
        }



        show() {
            this.view.innerHTML = this.content;
            //console.log("bluetoothpairing show called");
			
			const list = document.getElementById('extension-bluetoothpairing-list');
            const pre = document.getElementById('extension-bluetoothpairing-response-data');
            //const original = document.getElementById('extension-bluetoothpairing-original-item');
            //const list = document.getElementById('extension-bluetoothpairing-list');

            const leader_dropdown = document.querySelectorAll(' #extension-bluetoothpairing-view #extension-bluetoothpairing-original-item .extension-bluetoothpairing-thing1')[0];
            const highlight_dropdown = document.querySelectorAll(' #extension-bluetoothpairing-view #extension-bluetoothpairing-original-item .extension-bluetoothpairing-thing2')[0];

            pre.innerText = "";

            // Click event for ADD button
            document.getElementById("extension-bluetoothpairing-add-button").addEventListener('click', () => {
                //this.items_list.push({'enabled': false});
				document.getElementById('extension-bluetoothpairing-list').innerHTML = '<div class="extension-bluetoothpairing-spinner"><div></div><div></div><div></div><div></div></div>';
                this.scan();
            });

            // Get list of items
            window.API.postJson(
                `/extensions/${this.id}/api/init`

            ).then((body) => {
                //console.log("Python API result:");
                //console.log(body);
                //console.log(body['items']);
				//console.log(body['state']);
                if (body['state'] == 'ok' || body['state'] == true) {
                    this.items_list = body['items'];
                    this.regenerate_items();
                } else {
                    console.log("bluetoothpairing: not ok response while getting items list");
                    list.innerText = "Error during initialisation";
					
                }

            }).catch((e) => {
                //pre.innerText = e.toString();
                //console.log("bluetoothpairing: error in calling init via API handler");
                console.log("Bluetooth: Server error during init: " + e.toString());
                list.innerHTML = "Loading items failed - server error";
            });

        }

        scan() {
			
			const list = document.getElementById('extension-bluetoothpairing-list');
            // Get list of items
            window.API.postJson(
                `/extensions/${this.id}/api/scan`

            ).then((body) => {
                //console.log("Python API scan result:");
                //console.log(body);
                //console.log(body['items']);
                if (body['state'] == 'ok') {
                    this.items_list = body['items'];
                    this.regenerate_items();
                } else {
                    //console.log("not ok response while getting items list");
                    list.innerText = body['state'];
                }


            }).catch((e) => {
                //pre.innerText = e.toString();
                //console.log("bluetoothpairing: error in calling init via API handler");
                console.log("bluetoothpairing: scan error: " + e.toString());
                list.innerText = "Loading items failed - connection error";
            });
        }

        //
        //  REGENERATE ITEMS
        //

        regenerate_items() {

            //console.log("regenerating");
            //console.log(this.items_list);

            this.item_number = 0;
            //const leader_property_dropdown = document.querySelectorAll(' #extension-bluetoothpairing-view #extension-bluetoothpairing-original-item .extension-bluetoothpairing-property2')[0];
            //const highlight_property_dropdown = document.querySelectorAll(' #extension-bluetoothpairing-view #extension-bluetoothpairing-original-item .extension-bluetoothpairing-property2')[0];


            try {
                const items = this.items_list;

                const original = document.getElementById('extension-bluetoothpairing-original-item');
                const list = document.getElementById('extension-bluetoothpairing-list');
				const pre = document.getElementById('extension-bluetoothpairing-response-data');
                list.innerHTML = "";

                // Loop over all items
                for (var item in items) {
					//console.log(items[item]);
                    var clone = original.cloneNode(true);
                    clone.removeAttribute('id');

                    //console.log(items[item]['mac']);
                    
					const mac = items[item]['mac'];
                    const safe_mac = mac.replace(/:/g, "-");
                    clone.removeAttribute('id');
                    clone.setAttribute('id', safe_mac);

					//console.log("paired: " + items[item]['paired']);
					if( items[item]['paired'] == true ){
						//console.log("ENABLED");
						clone.classList.add("extension-bluetoothpairing-item-paired");
					}
					

					

                    // Change switch icon
                    clone.querySelectorAll('.switch-checkbox')[0].id = 'toggle' + this.item_number;
                    clone.querySelectorAll('.switch-slider')[0].htmlFor = 'toggle' + this.item_number;
                    this.item_number++;


                    // Pair button click event
                    const pair_button = clone.querySelectorAll('.extension-bluetoothpairing-item-pair-button')[0];
                    pair_button.addEventListener('click', (event) => {
                        //console.log("pair button clicked");
                        //console.log(event);
                        var target = event.currentTarget;
                        var main_item = target.parentElement.parentElement.parentElement; //parent of "target"
                        //console.log(main_item);
                        main_item.classList.add("extension-bluetoothpairing-item-pairing");
						const info_panel = main_item.querySelectorAll('.extension-bluetoothpairing-item-info')[0];

                        // Communicate with backend
                        window.API.postJson(
                            `/extensions/${this.id}/api/update`, {
                                'mac': mac,
                                'action': 'pair'
                            }
                        ).then((body) => {
                            //thing_list.innerText = body['state'];
                            //console.log(body);
                            if (body['state'] != 'ok') {
                                if( body['state'] == true ){
									main_item.classList.add("extension-bluetoothpairing-item-paired");
                                }
                                else if( body['state'] == false ){									
									main_item.classList.add("extension-bluetoothpairing-item-pairing-failed");
                                }
								else{
									pre.innerText = body['state'];
								}
                            }
							main_item.classList.remove("extension-bluetoothpairing-item-pairing");
							
							info_panel.innerHTML = "";
							
							for (var i = 0; i < body['update'].length; i++) {
								info_panel.innerHTML = info_panel.innerHTML + '<span class="">' + body['update'][i] + '</span>';
							}

                        }).catch((e) => {
                            console.log("bluetoothpairing: server connection error while pairing: " + e.toString());
                            pre.innerText = e.toString();
							info_panel.innerHTML = "Error connecting to server";
							main_item.classList.remove("extension-bluetoothpairing-item-pairing");
                        });
                    });


                    // Info button click event
                    const info_button = clone.querySelectorAll('.extension-bluetoothpairing-mac')[0];
                    info_button.addEventListener('click', (event) => {
                        //console.log("secret info button clicked");
                        //console.log(event);
                        var target = event.currentTarget;
                        var main_item = target.parentElement.parentElement.parentElement; //parent of "target"
                        //console.log(main_item);
                        //main_item.classList.add("info");

                        // Communicate with backend
                        window.API.postJson(
                            `/extensions/${this.id}/api/update`, {
                                'mac': mac,
                                'action': 'info'
                            }
                        ).then((body) => {
                            //thing_list.innerText = body['state'];
                            //console.log(body);
                            if (body['state'] != 'ok') {
                                pre.innerText = body['state'];
                            }
							
							const info_panel = main_item.querySelectorAll('.extension-bluetoothpairing-item-info')[0];
							info_panel.innerHTML = "";
							
							for (var i = 0; i < body['update'].length; i++) {
								info_panel.innerHTML = info_panel.innerHTML + '<span class="">' + body['update'][i] + '</span>';
							}

                        }).catch((e) => {
                            console.log("bluetoothpairing: server connection error while pairing: " + e.toString());
                            pre.innerText = e.toString();
                        });
                    });
					
                    // Add checkbox click event
                    const checkbox = clone.querySelectorAll('.switch-checkbox')[0];
                    checkbox.addEventListener('change', (event) => {

                        var target = event.currentTarget;
                        var main_item = target.parentElement.parentElement.parentElement; //parent of "target"
                        //console.log(main_item);

                        if (this.checked) {
                            //console.log("checkbox was UNchecked. Event:");
							//console.log(event);

                            // Communicate with backend
                            window.API.postJson(
                                `/extensions/${this.id}/api/update`, {
                                    'mac': mac,
                                    'action': 'unpair'
                                }
                            ).then((body) => {
                                //thing_list.innerText = body['state'];
                                //console.log(body); 
								
								const safe_mac = body['mac'].replace(/:/g, "-");
								main_item = document.getElementById(safe_mac);
								
                                if (body['state'] != 'ok') {
	                                if( body['state'] == false ){
										main_item.querySelectorAll('.extension-bluetoothpairing-enabled')[0].checked = body['state'];
	                                }
									else{
										pre.innerText = body['state'];
									}
                                }
								main_item.querySelectorAll('.extension-bluetoothpairing-item-info')[0].innerHTML = body['update'];

                            }).catch((e) => {
                                console.log("bluetoothpairing: server connection error while pairing: " + e.toString());
                                pre.innerText = e.toString();
                            });

                        } else {
                            //console.log("checkbox was checked. Event:");
							//console.log(event);
							
							main_item.classList.add("extension-bluetoothpairing-item-connecting");

                            // Communicate with backend
                            window.API.postJson(
                                `/extensions/${this.id}/api/update`, {
                                    'mac': mac,
                                    'action': 'connect'
                                }
                            ).then((body) => {
                                //thing_list.innerText = body['state'];
                                //console.log(body); 
								
								const safe_mac = body['mac'].replace(/:/g, "-");
								//console.log("safe_mac to find element ID = " + safe_mac);
								main_item = document.getElementById(safe_mac);
								//console.log("main_item:");
								//console.log(main_item);
                                if (body['state'] != 'ok') {
	                                if( body['state'] == false ){
										main_item.querySelectorAll('.extension-bluetoothpairing-enabled')[0].checked = body['state'];
	                                }
									else{
										pre.innerText = body['state'];
									}
                                }
								main_item.classList.remove("extension-bluetoothpairing-item-connecting");
								main_item.querySelectorAll('.extension-bluetoothpairing-item-info')[0].innerHTML = body['update'];
								

                            }).catch((e) => {
                                console.log("bluetoothpairing: server connection error while unpairing: " + e.toString());
                                pre.innerText = e.toString();
                            });
                        }
                    });
					
                    // Update to the actual values of regenerated item
                    for (var key in this.item_elements) { // name and mac
                        try {
                            if (this.item_elements[key] != 'enabled') {
                                clone.querySelectorAll('.extension-bluetoothpairing-' + this.item_elements[key])[0].innerText = items[item][this.item_elements[key]];
                            }
                        } catch (e) {
                            console.log("bluetoothpairing: could not regenerate actual values of highlight: " + e);
                        }
                    }

                    // Set enabled state of regenerated item
                    
					if (items[item]['connected'] == true) {
                        //clone.querySelectorAll('.extension-bluetoothpairing-enabled')[0].removeAttribute('checked');
                        clone.querySelectorAll('.extension-bluetoothpairing-enabled')[0].checked = items[item]['connected'];
                    }
					
					
                    if( safe_mac == items[item]['name'] ){
                    	list.append(clone);
                    }
					else{
						list.prepend(clone);
					}
					
                }
				

            } catch (e) {
                console.log("bluetoothpairing: error regenerating: " + e);
            }
        }

		hide(){
			//console.log("hiding bluetooth extension");
			this.view.innerHTML = "";
			
            // Get list of items
            window.API.postJson(
                `/extensions/${this.id}/api/exit`

            ).then((body) => {
                //console.log("Python API exit result:");
                //console.log(body);
                /*
				if (body['state'] == 'ok' || body['state'] == true) {
					console.log("exited cleanly");
                } else {
                    console.log("not ok response while getting items list");
                }
				*/

            }).catch((e) => {
                console.log("bluetoothpairing: server error during exit: " + e.toString());
            });
			
		}

    }

    new Bluetoothpairing();

})();