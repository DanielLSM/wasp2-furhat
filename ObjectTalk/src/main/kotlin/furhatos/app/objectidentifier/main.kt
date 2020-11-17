package furhatos.app.objectidentifier

import furhatos.app.objectidentifer.getConnectedSocket
import furhatos.app.objectidentifier.flow.EnterEvent
import furhatos.app.objectidentifier.flow.LeaveEvent
import furhatos.app.objectidentifier.flow.Main
import furhatos.event.EventSystem
import furhatos.skills.Skill
import furhatos.flow.kotlin.*
import furhatos.util.CommonUtils
import org.zeromq.ZMQ
import kotlinx.coroutines.launch
import kotlinx.coroutines.GlobalScope
import zmq.ZMQ.ZMQ_SUB

val logger = CommonUtils.getRootLogger()
val objserv = "tcp://127.0.0.1:9999" //The TCP socket of the object server
val languageserv = "tcp://127.0.0.1:9998" //The TCP socket of the object server


val subSocket: ZMQ.Socket = getConnectedSocket(ZMQ_SUB, objserv) //Makes a socket of the object server
val subSocket1: ZMQ.Socket = getConnectedSocket(ZMQ_SUB, languageserv) //Makes a socket of the object server

val enter = "enter_" //Objects that enter the view start with this string
val leave = "leave_" //Objects that leave the view start with this string

/**
 * Parses a message from the object server, turns the message into a list of objects.
 */
fun getObjects(message: String, delimiter: String): List<String> {
    val objects = mutableListOf<String>()
    message.split(" ").forEach {
        if(it.startsWith(delimiter)) {
            objects.add(it.removePrefix(delimiter))
        }
    }
    return objects
}

/**
 * Function that starts a thread which continuously polls the object server.
 * Based on what is in the message will either send:
 *  - EnterEvent, for objects coming into view.
 *  - LeaveEvent, for objects going out of view.
 *
 *  These events can be caught in the flow (Main), and be responded to.
 */
fun startListenThread() {
    GlobalScope.launch { // launch a new coroutine in background and continue
        logger.warn("LAUNCHING COROUTINE")
        subSocket.subscribe("")
        subSocket1.subscribe("")
        while (true) {
            val message = subSocket.recvStr()
            val language = subSocket1.recvStr()
            logger.warn("got: $message")
            EventSystem.send(EnterEvent(message,language))
        }
    }
}

class ObjectIdentifierSkill : Skill() {
    override fun start() {
        startListenThread()
        Flow().run(Main)
    }
}

fun main(args: Array<String>) {
    Skill.main(args)
}
