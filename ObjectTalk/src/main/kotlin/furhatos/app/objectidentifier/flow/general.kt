package furhatos.app.objectidentifier.flow

import furhatos.event.Event
import furhatos.flow.kotlin.furhat
import furhatos.flow.kotlin.state

import furhatos.util.Language

/**
 * Events used for communication between the thread and the flow.
 */
class EnterEvent(val message: String, val language: String): Event()
class LeaveEvent(val objects: List<String>): Event()

/**
 * Main flow that starts the camera feed and awaits events sent from the thread
 */
val Main = state {

    onEntry {
        furhat.cameraFeed.enable()
        furhat.setVoice(language=Language.ENGLISH_US)
        furhat.say("Welcome to this camera feed demonstration, please place an item in front of me. Maybe I can detect what it is.")
    }

    onEvent<EnterEvent> {// Objects that enter the view
        if (it.language == "en"){
            furhat.setVoice(language=Language.ENGLISH_US)
        }
        if (it.language == "fr"){
            furhat.setVoice(language=Language.FRENCH)
        }
        if (it.language == "sv"){
            furhat.setVoice(language=Language.SWEDISH)
        }

        furhat.say(it.message)
    }

    onEvent<LeaveEvent> {
        if (it.objects.size > 1) { //Objects that leave the view
            furhat.say("You removed multiple objects. ${it.objects.joinToString(" and ")}")
        } else {
            furhat.say("No, don't remove that, I love the ${it.objects[0]}")
        }
    }

    onExit {
        furhat.cameraFeed.disable()
    }
}