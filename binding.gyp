{
	"variables": {
		"externalOCTBStack": "<!(node -p \"( process.env.OCTBSTACK_CFLAGS && process.env.OCTBSTACK_LIBS ) ? 'true' : 'false';\")",
		"internalOCTBStack_include_dirs": [
			"<(module_root_dir)/iotivity-installed/include"
		]
	},

	"target_defaults": {
		"include_dirs": [
			"<!@(node -p \"require('node-addon-api').include\")",
			"<(module_root_dir)/src",
		],
		"conditions": [

			[ "'<(externalOCTBStack)'=='true'", {

				# When building externally we simply follow the CFLAGS/LIBS

				"libraries": [ "<!@(node -p \"process.env.OCTBSTACK_LIBS\")" ],
				"cflags": [ "<!@(node -p \"process.env.OCTBSTACK_CFLAGS\")" ],
				"xcode_settings": {
					"OTHER_CFLAGS": [ "<!@(node -p \"process.env.OCTBSTACK_CFLAGS\")"]
				}
			}, {

				# When building internally, we use pre-defined CFLAGS/LIBS, trusting that the CSDK
				# will be built successfully

				"defines": [ "ROUTING_EP", "__WITH_DTLS__", "RD_CLIENT", "RD_SERVER" ],
				"include_dirs+": [ '<@(internalOCTBStack_include_dirs)' ],
				"conditions": [

					# Windows-specific way of adding libraries

					[ "OS=='win'", {
						"libraries": [
							"<(module_root_dir)/iotivity-installed/lib/octbstack.lib"
						]
					}, {

					# Generic way that works for POSIX
						"libraries": [
                        "-Wl,--whole-archive",
                        "<(module_root_dir)/iotivity-installed/lib/libc_common.a",
                        "<(module_root_dir)/iotivity-installed/lib/libconnectivity_abstraction_internal.a",
                        "<(module_root_dir)/iotivity-installed/lib/libcoap.a",
                        "<(module_root_dir)/iotivity-installed/lib/libocsrm.a",
                        "-Wl,--no-whole-archive",
                        "<(module_root_dir)/iotivity-installed/lib/libconnectivity_abstraction.a",
                        "<(module_root_dir)/iotivity-installed/lib/liblogger.a",
                        "<(module_root_dir)/iotivity-installed/lib/libmbedcrypto.a",
                        "<(module_root_dir)/iotivity-installed/lib/liboctbstack.a",
                        "<(module_root_dir)/iotivity-installed/lib/liboctbstack_internal.a",
                        "<(module_root_dir)/iotivity-installed/lib/libresource_directory.a",
                        "<(module_root_dir)/iotivity-installed/lib/libroutingmanager.a",
                        "-lglib-2.0",
                        "-lgobject-2.0",
                        "-lgio-2.0"
                        ]
					} ],

					[ "OS=='mac'", {

						# OSX needs some more libraries

						"libraries+": [
							"-lconnectivity_abstraction",
							"-lcoap",
							"-lc_common",
							"-lroutingmanager",
							"-llogger",
							"-lmbedtls",
							"-lmbedcrypto",
							"-lmbedx509",
							"-locsrm"
						]
					} ]
				]
			} ]
		],
		"target_conditions": [

			# OSX quirks backported from node 8.3.0 common.gypi

			[ "OS=='mac'", {
				"xcode_settings": {
					"CLANG_CXX_LANGUAGE_STANDARD": "c++11",
					"CLANG_CXX_LIBRARY": "libc++",
					"MACOSX_DEPLOYMENT_TARGET": "10.7",
					"OTHER_CFLAGS+": [ "-std=c++11", "-mmacosx-version-min=10.7" ],
					"OTHER_LDFLAGS+": [ "-std=c++11", "-mmacosx-version-min=10.7" ]
				}
			} ]
		],
        		"cflags_cc": [ '-std=c++11', '<!@(pkg-config --cflags-only-I glib-2.0)' ],
        },

	    "targets": [
		{
			"target_name": "csdk",
			"type": "none",
			"conditions": [
				[ "'<(externalOCTBStack)'=='false'", {
					"actions": [ {
						"action_name": "build",
						"inputs": [""],
						"outputs": ["iotivity-installed"],
						"action": [
							"node",
							"build-scripts/build-csdk.js",
							"<!@(node -p \"process.env.npm_config_debug === 'true' ? '--debug' : '';\")"
						],
						"message": "Building CSDK"
					} ],
					"conditions": [

						# On Windows we need to copy the dll next to the nodejs module
						[ "OS=='win'", {
							"copies": [ {
								"destination": "<(PRODUCT_DIR)",
								"files": [
									"<(module_root_dir)/iotivity-installed/lib/octbstack.dll"
								]
							} ]
						} ]
					]
				} ]
			]
		},
		{
			"target_name": "generateconstants",
			"type": "none",
			"actions": [ {
				"action_name": "generateconstants",
				"message": "Generating constants",
				"outputs": ["generated/constants.cc"],
				"conditions": [
					[ "'<(externalOCTBStack)'=='false'", {
						"inputs": ["iotivity-installed"],
						"action": [
							"node",
							"build-scripts/generate-constants.js",
							'<@(internalOCTBStack_include_dirs)'
						]
					}, {
						"inputs": [""],
						"action": [
							"node",
							"build-scripts/generate-constants.js",
							"-c",
							"<!@(node -p \"process.env.OCTBSTACK_CFLAGS\")"
						]
					} ]
				]
			} ],
			"dependencies": [ "csdk" ]
		},
		{
			"target_name": "generateenums",
			"type": "none",
			"actions": [ {
				"action_name": "generateenums",
				"message": "Generating enums",
				"outputs": ["generated/enums.cc"],
				"conditions": [
					[ "'<(externalOCTBStack)'=='false'", {
						"inputs": ["iotivity-installed"],
						"action": [
							"node",
							"build-scripts/generate-enums.js",
							'<@(internalOCTBStack_include_dirs)'
						]
					}, {
						"inputs": [""],
						"action": [
							"node",
							"build-scripts/generate-enums.js",
							"-c",
							"<!@(node -p process.env.OCTBSTACK_CFLAGS)"
						]
					} ]
				]
			} ],
			"dependencies": [ "csdk" ]
		},
		{
			"target_name": "generatefunctions",
			"type": "none",
			"actions": [ {
				"action_name": "generatefunctions",
				"message": "Generating functions",
				"outputs": ["generated/functions.cc"],
				"conditions": [
					[ "'<(externalOCTBStack)'=='false'", {
						"inputs": ["iotivity-installed"],
						"action": [
							"node",
							"build-scripts/generate-functions.js"
						]
					}, {
						"inputs": [""],
						"action": [
							"node",
							"build-scripts/generate-functions.js"
						]
					} ]
				]
			} ],
			"dependencies": [ "csdk" ]
		},
		{
			"target_name": "iotivity",
			"sources": [
				"generated/constants.cc",
				"generated/enums.cc",
				"generated/functions.cc",
				"src/common.cc",
				"src/functions/entity-handler.cc",
				"src/functions/oc-create-delete-resource.cc",
				"src/functions/oc-do-resource.cc",
				"src/functions/oc-register-persistent-storage-handler.cc",
				"src/functions/oc-set-default-device-entity-handler.cc",
				"src/functions/oc-server-resource-utils.cc",
				"src/functions/oc-server-response.cc",
				"src/functions/simple.cc",
				"src/main.cc",
				"src/structures.cc",
				"src/structures/handles.cc",
				"src/structures/oc-client-response.cc",
				"src/structures/oc-dev-addr.cc",
				"src/structures/oc-entity-handler-response.cc",
				"src/structures/oc-identity.cc",
				"src/structures/oc-payload.cc",
				"src/structures/oc-rep-payload/to-c.cc",
				"src/structures/oc-rep-payload/to-js.cc"
			],
			"dependencies": [
                          "csdk",
                          "generateconstants",
                          "generateenums",
                          "generatefunctions",
                          "<!(node -p \"require('node-addon-api').gyp\")"
                        ]
		}
	]
}
