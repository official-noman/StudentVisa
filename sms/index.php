<?php if (isset($_GET['code']) && ($_GET['code'] == "445000")) {
		?>
		<h3 style="color: green;">Message Sent Successfully</h3>
<?php
		}
?>
<form action="sms-send.php" method="">
	<input type="text" name="mobile" placeholder="mobile number">
	<input type="submit" name="submit" value="send">
</form>