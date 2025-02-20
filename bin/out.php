<?php

$path_data = '../data';
$path_media = $path_data . '/media';

$file_cookie = $path_data . '/cookie.txt';
$file_host = $path_data . '/host.txt';
$file_imagehost = $path_data . '/imagehost.txt';
$file_vod = $path_data . '/vod.txt';

$path_dist = '../dist';
$file_all_json = $path_dist . '/all.json';

$imagehost = 'https://666546.xyz';
$imagehost = @file_get_contents($file_imagehost);

$arr = glob($path_media . '/*', GLOB_MARK | GLOB_NOSORT);
natsort($arr);
$arr = array_reverse($arr);

$all = [];
$count = 0;
foreach ($arr as $key => $value) {
	if ($count > 10) {
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
	}
	$count++;
}

file_put_contents($file_all_json, json_encode($all, JSON_UNESCAPED_UNICODE));
var_dump('out.php run over! count: ' . count($all));
