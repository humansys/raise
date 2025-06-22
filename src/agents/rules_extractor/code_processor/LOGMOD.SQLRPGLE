**FREE
Ctl-Opt NOMAIN;

  /Copy QRPGLEREF,SISCPYBK

  Dcl-Proc firstLogin Export;
    Dcl-Pi firstLogin LIKEDS(passbys);
      logged zoned(1:0);
    End-Pi;
    Dcl-S password1 char(10);

    Dcl-DS passbys1 LIKEDS(passbys);
//varibles

    clear usrnme;
    clear pwd;
    clear password1;

    Write Header;
    Write Footer;

    If (logged = 1);    //User is previously logged in, and exits to login screen
      Exfmt logoutwin;
      logged = 0;
    ENDIF;

    Exfmt logscrn;
    Exec SQL
      Set Option Commit = *None;

    Exec SQL
      Select PASSWORD Into :password1
        From USERS
        Where username = :USRNME;

   If (SQLCode = 0 AND PWD = password1);           //*ZERO
      passbys1.returncode = 000;
      passbys1.username1 = usrnme;
      password1 = *BLANK;
      clear logmsg;

   ElseIf (SQLCode = 0 AND PWD <> password1);    //*ZERO
      passbys1.returncode = 100;
      LogMSG = 'Incorrect password';
   Else;
      passbys1.returncode = 100;
      LogMsg = 'User does not exist';
   EndIf;

 //Indicators
   If (exit = *on);                            //If user presses F3 on login screen
     passbys1.returncode = 111;

   ElseIf (refresh = *on);
      clear Logmsg;
      clear usrnme;
      clear pwd;
      passbys1.returncode = 100;
   ENDIF;

   return passbys1;
  End-Proc; 