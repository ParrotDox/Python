def FormatMsg(msg,l):
    msgLen = len(msg)
    if(msgLen > l):
        ind = 0
        formattedMsg = ""
        while(ind < msgLen - 1):
            if(ind + l >= msgLen):
                formattedMsg += " " + msg[ind:msgLen]
                ind += msgLen
                break
            formattedMsg += " " + msg[ind:ind + l] + '\n'
            ind += l
        return formattedMsg
    else:
        return msg

#Simple header/footer
def HeadFoot(hdr):
    line = len(hdr) - 2
    print("+" + line * "-" + "+")
    return line

#Header
header = "This program is used to check I/O"
print(header)
line = HeadFoot(header)
#Text and formatting
text = "Sam squinted against the sun at the distant dust trail raked up by the car on its way up to the Big House. The horses kicked and flicked their tails at flies, not caring about their owner's first visit in ten months. Sam waited. Mr Carter didn't come out here unless he had to, which was just fine by Sam. The more he kept out of his boss's way, the longer he'd have a job."
print(FormatMsg(text, line), end="")
#Footer
HeadFoot(header)

