[dial-@cid]
exten => dial,1,Noop()
 same => n,Dial(SIP/voip-ast/${NUMBER})
 same => n,Hangup()

exten => h,1,Noop(${DIALSTATUS} - ${HANGUPCAUSE})
 same => n,Set(ODBC_UPDATECALL(${ID})=${DIALSTATUS})

[message-@cid]
exten => 1,1,Noop("Number 1 pressed")
 same => n,Playback(yandex/youllbecalled)
 same => n,Playback(yandex/thankyou)
 same => n,Set(ODBC_NEEDREDIAL(${ID})=1)
 same => n,Hangup()

exten => s,1,Noop(${ID} ${VAR2})
 same => n,Answer()
 same => n,Wait(2)
 same => n,Playback(yandex/zdravstvyite)
 same => n,Playback(yandex/names/@namefile)
 same => n,Playback(yandex/oftalmolog)
 same => n,Playback(yandex/dates/@datefile)
 same => n,Playback(yandex/times/@timefile)
 same => n,Playback(yandex/address)
 same => n,Background(yandex/pressone)
 same => n,WaitExten(3)
 same => n,Playback(yandex/thankyou)
 same => n,Hangup()
