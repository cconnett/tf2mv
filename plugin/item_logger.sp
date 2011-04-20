#pragma semicolon 1

#include <sourcemod>

#define PLUGIN_VERSION  "1.0"

public Plugin:myinfo =
{
	name = "Trading Logger",
	author = "AlphaChannel",
	description = "Log all trade items recieved on the server",
	version = PLUGIN_VERSION,
	url = "http://tf2mv.net"
};

public OnPluginStart()
{
	CreateConVar("sm_itemlogger", PLUGIN_VERSION, "Item Found Logger plugin Version", FCVAR_PLUGIN|FCVAR_SPONLY|FCVAR_REPLICATED|FCVAR_NOTIFY);

	HookEvent("item_found", Event_ItemFound);
}

public Action:Event_ItemFound(Handle:event, const String:name[], bool:dontBroadcast)
{
	decl String:date[64];
	FormatTime(date, sizeof(date), "%x %X", GetTime());

	new userid = GetEventInt(event, "player");
	new String:steamid[64];
	GetClientAuthString(userid, steamid, sizeof(steamid));

	new method = GetEventInt(event, "method");
	new quality = GetEventInt(event, "quality");
	new String:item[64];
	GetEventString(event, "item", item, sizeof(item));

	LogToGame("TF2MV:%s;%s;%d;%d;%s", date, steamid, method, quality, item);
}
