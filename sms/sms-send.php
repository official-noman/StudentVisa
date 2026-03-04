<?php

        if (isset($_GET['submit'])) {
        $mobile_number = $_GET['mobile'];

        $message = "Hello How Are You?";

        $message = urlencode($message);

        $mobile_number = $mobile_number;
        $api_key = '445156057064961560570649';
        $sender_id = '8801844532630';
        $sender_id = urlencode($sender_id);

        $url = "http://sms.iglweb.com/api/v1/send?api_key=".$api_key."&contacts=".$mobile_number."&senderid=". $sender_id ."&msg=".$message;

        }
        //var_dump($url);
        $ch_banpage = curl_init($url);
        // var_dump($ch_banpage);

        curl_setopt($ch_banpage, CURLOPT_URL, $url);
        curl_setopt($ch_banpage, CURLOPT_HEADER, 0);
        curl_setopt($ch_banpage, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch_banpage, CURLOPT_SSL_VERIFYPEER, false);
        

        $curl_scraped_page = curl_exec($ch_banpage);
        
        if (curl_errno($ch_banpage)) {

            $error_msg = curl_error($ch_banpage);
            // var_dump($error_msg);
        } 
        if(!isset($error_msg)){
            $api_response = json_decode($curl_scraped_page);
            if ($api_response->code == "445000") {
                $msg = "SMS Sending Successfully!";
            } else if ($api_response->code == "445040") {
                $msg = "SMS Sending failed because of invalid API key";
            } else if ($api_response->code == "445080") {
                $msg = "SMS Sending failed because of invalid Sender ID";
            } else if ($api_response->code == "445120") {
                $msg = "SMS Sending failed because of your sms balance is low";
            } else if ($api_response->code == "445110") {
                $msg = "SMS Sending failed because of Client number are invalid";
            } else {
                $msg = "SMS Sending failed because of ". $api_response;
            }
        }else {
            $msg = $error_msg;
        }
        // var_dump($curl_scraped_page);
        // die("a");
        curl_close($ch_banpage);
        $message = urlencode($msg);
        header('Location:index.php?code='.$api_response->code."&message=".$message);
 ?>