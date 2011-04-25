#pragma semicolon 1

#include <sourcemod>
#include <cURL>

public Plugin:myinfo = {
	name = "item_found Logger",
	author = "Chris 'AlphaChannel' Connett <plugin@tf2mv.com>",
	description = "Log all item_found events to a webservice.",
	version = PLUGIN_VERSION,
	url = "http://tf2mv.com/plugin"
};

new CURL_Default_opt[][2] = {
	{_:CURLOPT_NOSIGNAL,1},
	{_:CURLOPT_NOPROGRESS,1},
	{_:CURLOPT_TIMEOUT,10},
	{_:CURLOPT_CONNECTTIMEOUT,15},
	{_:CURLOPT_VERBOSE,0}
};

#define CURL_DEFAULT_OPT(%1) curl_easy_setopt_int_array(%1, CURL_Default_opt, sizeof(CURL_Default_opt))

public OnPluginStart() {
	CreateConVar("sm_itemlogger", PLUGIN_VERSION, "Item Found Logger plugin Version", FCVAR_PLUGIN|FCVAR_SPONLY|FCVAR_REPLICATED|FCVAR_NOTIFY);

	HookEvent("item_found", Event_ItemFound);
}

public Action:Event_ItemFound(Handle:event, const String:name[], bool:dontBroadcast) {
	new String:steamid[64];
	new String:method[16];
        new String:quality[16];
        new String:propername[16];
	new String:item[64];

	GetClientAuthString(GetEventInt(event, "player"), steamid, sizeof(steamid));
        Format(method, sizeof(method), "%d", GetEventInt(event, "method"));
	Format(quality, sizeof(quality), "%d", GetEventInt(event, "quality"));
	Format(propername, sizeof(propername), "%d", GetEventBool(event, "propername"));
	GetEventString(event, "item", item, sizeof(item));

        new Handle:formpost = INVALID_HANDLE;
        formpost = curl_httppost();
        curl_formadd(formpost,
                     CURLFORM_COPYNAME, "steamid",
                     CURLFORM_COPYCONTENTS, steamid,
                     CURLFORM_END);
        curl_formadd(formpost,
                     CURLFORM_COPYNAME, "method",
                     CURLFORM_COPYCONTENTS, method,
                     CURLFORM_END);
        curl_formadd(formpost,
                     CURLFORM_COPYNAME, "quality",
                     CURLFORM_COPYCONTENTS, quality,
                     CURLFORM_END);
        curl_formadd(formpost,
                     CURLFORM_COPYNAME, "item",
                     CURLFORM_COPYCONTENTS, item,
                     CURLFORM_END);
        curl_formadd(formpost,
                     CURLFORM_COPYNAME, "propername",
                     CURLFORM_COPYCONTENTS, propername,
                     CURLFORM_END);

        new Handle:curl = INVALID_HANDLE;
        curl = curl_easy_init();
        if (curl != INVALID_HANDLE) {

          CURL_DEFAULT_OPT(curl);

          new Handle:headerlist = curl_slist();
          curl_slist_append(headerlist, "Expect:");

          curl_easy_setopt_int(curl, CURLOPT_POST, 1);
          curl_easy_setopt_handle(curl, CURLOPT_HTTPHEADER, headerlist);
          curl_easy_setopt_string(curl, CURLOPT_URL, TARGET_URL);
          curl_easy_setopt_int(curl, CURLOPT_PORT, TARGET_PORT);
          curl_easy_setopt_handle(curl, CURLOPT_HTTPPOST, formpost);
          curl_easy_perform_thread(curl, onComplete);
        }

        return Plugin_Continue;
}

public onComplete(Handle:hndl, CURLcode: code, any:data) {
	if(code != CURLE_OK) {
		new String:error_buffer[256];
		curl_easy_strerror(code, error_buffer, sizeof(error_buffer));
	}

	CloseHandle(hndl);
        //CloseHandle(formpost);
}
