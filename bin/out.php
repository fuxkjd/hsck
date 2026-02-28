<?php

$path_data = '..' . DIRECTORY_SEPARATOR . 'data';
$path_media = $path_data . DIRECTORY_SEPARATOR . 'media';

$file_cookie = $path_data . DIRECTORY_SEPARATOR . 'cookie.txt';
$file_host = $path_data . DIRECTORY_SEPARATOR . 'host.txt';
$file_imagehost = $path_data . DIRECTORY_SEPARATOR . 'imagehost.txt';
$file_vod = $path_data . DIRECTORY_SEPARATOR . 'vod.txt';

$path_dist = '..' . DIRECTORY_SEPARATOR . 'dist';
$file_all_json = $path_dist . DIRECTORY_SEPARATOR . 'all.json';
$file_all_txt = $path_dist . DIRECTORY_SEPARATOR . 'all.txt';
$file_all_m3u = $path_dist . DIRECTORY_SEPARATOR . 'all.m3u';

$imagehost = 'https://666546.xyz';
$imagehost = @file_get_contents($file_imagehost);

$arr = glob($path_media . DIRECTORY_SEPARATOR . '*', GLOB_MARK | GLOB_NOSORT);
natsort($arr);
$arr = array_reverse($arr);

$all = [];
$txt = '';
$m3u = "#EXTM3U\n";
$m3uGroup = '';
$count = 0;
$num = 0;
foreach ($arr as $key => $value) {
	if ($count > 20) {
		// 删除目录中的所有文件和子目录
		$arr_json = glob($value . '*.json', GLOB_NOSORT);
		foreach ($arr_json as $k => $v) {
			@unlink($v);
		}
		@rmdir($value);
		continue;
	}
	$arr_json = glob($value . '*.json', GLOB_NOSORT);
	natsort($arr_json);
	$arr_json = array_reverse($arr_json);
	foreach ($arr_json as $k => $v) {
		// var_dump($v);
		$cont = file_get_contents($v);
		$cont = json_decode($cont, true);
		if (!isset($cont['title']) || !isset($cont['thumd'])  || !isset($cont['media'])) {
			var_dump('error 出错文件，自动跳过 ' . $v);
			continue;
		}

		$cont['thumd'] = base64_encode($imagehost . base64_decode($cont['thumd']));
		$all[] = $cont;
		// 取 $num / 20 的余数，如果等于 0，则输出 $num
		if ($num % 20 == 0) {
			$txt = $txt . ($num + 1) . '-' . ($num + 20) . ",#genre#\n";
			$m3uGroup = ($num + 1) . '-' . ($num + 20);
		}
		$txt = $txt . base64_decode($cont['title']) . ',' . base64_decode($cont['media']) . "\n";
		$m3u = $m3u . "#EXTINF:-1 tvg-logo=\"" . base64_decode($cont['thumd']) . "\" group-title=\"" . $m3uGroup . "\", " . base64_decode($cont['title']) . "\n" . base64_decode($cont['media']) . "\n";
		$num++;
	}
	$count++;
}

file_put_contents($file_all_json, json_encode($all, JSON_UNESCAPED_UNICODE));
file_put_contents($file_all_txt, $txt);
file_put_contents($file_all_m3u, $m3u);
var_dump('out.php run over! count: ' . count($all) . ' num: ' . $num);
