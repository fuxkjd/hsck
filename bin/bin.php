<?php


$path_data = '../data';
$path_media = $path_data . '/media';

$file_host = $path_data . '/host.txt';
$file_imagehost = $path_data . '/imagehost.txt';
$file_vod = $path_data . '/vod.txt';

$host = '';
$imagehost = '';
$vod_list_max = [];

$cookie = '572a0a9982db70b0b107d638369b0b95=81188b3b7556baf6e51ad1fd9c9c1e37';

$wxpusher_apptoken = '';

/**
 * 获取 html
 */
function getHtml(string $url): string
{
    try {
        global $cookie;
        $body = shell_exec('curl --connect-timeout 10 -m 30 -H "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36" -k --cookie "' . $cookie . '" ' . $url . '  2>&1');

        return $body ?: '';
    } catch (\Throwable $th) {
        //throw $th;
    }
    return '';
}

/**
 * 获取普通页面的 header
 */
function getHeader(string $url): string
{
    try {
        $header = shell_exec('curl  --connect-timeout 10 -m 30 -H "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36" -k -I ' . $url . '  2>&1');

        return $header ?: '';
    } catch (\Throwable $th) {
        //throw $th;
    }
    return '';
}

/**
 * 获取验证码页面的 header
 */
function getHeader2(string $url, string $host): string
{
    try {
        $curl = 'curl  --connect-timeout 10 -m 30 -H "User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36" -k --referer ' . $host . '/ -I ' . $url;
        $header = shell_exec($curl);
        return $header ?: '';
    } catch (\Throwable $th) {
        //throw $th;
    }
    return '';
}

/**
 * 递归检查当前域名
 */
function checkHost(): bool
{
    global $file_host;
    $tmp_host = "http://hsck.us";
    $tmp_host = @file_get_contents($file_host);
    while (true) {
        $ret = checkHostContent($tmp_host);
        if ($ret === true) {
            file_put_contents($file_host, $tmp_host);
            global $host;
            $host = $tmp_host;
            return true;
        } elseif ($ret && is_string($ret)) {
            $tmp_host = $ret;
        } else {
            return false;
        }
    }
}

function stringToHex($str): string
{
    $val = '';
    for ($i = 0; $i < strlen($str); $i++) {
        $val .= strval(ord($str[$i]) + 1);
    }
    return $val;
}

/**
 * 检查域名正文类型
 */
function checkHostContent(string $tmp_host)
{
    echo "[debug] host check {$tmp_host}\n";
    $html = getHtml($tmp_host);
    if (strlen($html) > 20000 && strstr($html, "stui-warp-content")) {
        $ret = strstr($html, "最近更新");
        if ($ret) {
            $num = preg_match_all('/\/vodtype\/(\d+)\.html"><span\sclass="count\spull-right">(\d+)<\/span>/', $html, $matches);
            if ($num) {
                global $vod_list_max;
                for ($i = 0; $i < $num; $i++) {
                    $vod_list_max[$matches[1][$i]] = ['num' => $matches[2][$i], 'page' => ceil($matches[2][$i] / 40)];
                }

                // 检查封面图片域名
                if (preg_match('/stui-vodlist__thumb\slazyload"\shref="\/vodplay\/\d+-1-1\.html"\stitle="[^"]+"\sdata-original="(https?:\/\/[^\/]+)\/images\/[^"]+">/', $html, $matches)) {
                    global $imagehost;
                    $imagehost = $matches[1];
                    echo "[debug] images host: {$imagehost}\n";
                } else {
                    echo "[error] images host get error!\n";
                    return false;
                }
                return true;
            }
        }
    }
    if (strstr($html, 'strU=') && strstr($html, 'id="hao123"')) {
        $num = preg_match('/strU="(https?:\/\/[a-zA-Z0-9:\/\.]+\?u=?)"/', $html, $matches);
        if ($num) {
            $url = $matches[1] . "{$tmp_host}/&p=/";
            try {
                echo "[debug] host jump {$url}\n";
                $html = getHeader($url);
                $num = preg_match('/Location: (http:\/\/[a-zA-Z0-9]+\.[a-zA-Z0-9]+)/', $html, $matches);
                if ($num) {
                    return $matches[1];
                }
            } catch (\Throwable $th) {
                //throw $th;
            }
        }
    }

    if (strstr($html, '滑动验证')) {
        $num = preg_match('/src="(\/huadong.*js\?id=\w+)"/', $html, $matches);

        if ($num) {
            $js_url = $tmp_host . $matches[1];
            var_dump($js_url);
            $js_html = getHtml($js_url);
            $num = preg_match('/key="(\w+)",value="(\w+)"/', $js_html, $matches);

            if ($num) {
                $key = $matches[1];
                $value = $matches[2];
                $num = preg_match('/"(\/[\w\_]+yanzheng_huadong.php[\w_=\?]+&key=)"/', $js_html, $matches);
                if ($num) {
                    $yanzheng_url = $tmp_host . $matches[1] . $key . '&value=' . md5(stringToHex($value));

                    $yanzheng_url = addcslashes($yanzheng_url, '?=&');

                    $header = getHeader2($yanzheng_url, $tmp_host);

                    $num = preg_match('/Set-Cookie: ([\w\=]+);/', $header, $matches);
                    if ($num) {
                        global $cookie;
                        $cookie = $matches[1];
                        var_dump('new cookie: ' . $cookie);
                        return $tmp_host;
                    } else {
                        var_dump($header);
                        echo "js header cookie preg error!\n";
                    }
                } else {
                    var_dump($js_html);
                    echo "js yanzheng_url preg error!\n";
                }
            } else {
                var_dump($js_html);
                echo "js key/value preg error!\n";
            }
        }
    } else {
        var_dump($html);
        echo "host check error no rule...\n";
    }
    return false;
}

function getHost(): string
{
    global $host;
    return $host;
}

function getPageNum(int $id): int
{
    return ceil($id / 100);
}

function getListArr(int $vod_type_id, string $vod_type_name, int $page, int $max_page): bool
{
    echo "[debug] fetch vod_type: {$vod_type_id} {$vod_type_name} page: {$page} max_page: {$max_page}\n";
    $url = getHost() . "/vodtype/{$vod_type_id}-{$page}.html";
    $list_html = getHtml($url);

    $num = preg_match_all('/stui-vodlist__thumb\slazyload"\shref="(\/vodplay\/(\d+)-1-1\.html)"\stitle="([^"]+)"\sdata-original="(https?:\/\/[^"]+)">/u', $list_html, $matches);
    if (!$num) {
        echo "[error] vod_list preg match error! vod_type: {$vod_type_id} {$vod_type_name} page: {$page} max_page: {$max_page}\n";
        echo $list_html;
        return false;
    }

    preg_match_all('/pic-text text-right">([\d\:]+)</', $list_html, $matches_time);
    preg_match_all('/fa-heart"><\/i>&nbsp;(\d+)\s?&nbsp;&nbsp;</', $list_html, $matches_heart);
    preg_match_all('/fa-eye"><\/i>&nbsp;(\d+)\s?&nbsp;&nbsp;</', $list_html, $matches_eye);

    global $path_media;

    for ($i = 0; $i < $num; $i++) {
        $data = [];
        $data['vod_type_id'] = $vod_type_id;
        $data['vod_type_name'] = $vod_type_name;
        $data['vod_id'] = $matches[2][$i];
        $data['title'] = $matches[3][$i];
        $data['time'] = $matches_time[1][$i] ?? '';
        $data['heart'] = $matches_heart[1][$i] ?? 0;
        $data['eye'] = $matches_eye[1][$i] ?? 0;
        $vod_play_url =  $matches[1][$i];
        $content_url = getHost() . $vod_play_url;
        $data['thumd'] = $matches[4][$i];

        $path_vod_id = $path_media . "/" . getPageNum($data['vod_id']) . "/";
        if (!is_dir($path_vod_id)) {
            mkdir($path_vod_id, 0777, true);
        }
        $file_vod_id_json = $path_vod_id . "{$data['vod_id']}.json";
        if (is_file($file_vod_id_json)) {
            $cont = file_get_contents($file_vod_id_json);
            $cont = json_decode($cont, true);
            if ($cont['heart'] != $data['heart'] || $cont['eye'] != $data['eye']) {
                $cont['heart'] = $data['heart'];
                $cont['eye'] = $data['eye'];
                file_put_contents($file_vod_id_json, json_encode($cont, JSON_UNESCAPED_UNICODE));
                echo "[debug] vod_type: {$vod_type_id} {$vod_type_name} page: {$page} max_page: {$max_page} child_i: $i vod_id: {$data['vod_id']} update json file heart | eye ~ \n";
            } else {
                echo "[debug] vod_type: {$vod_type_id} {$vod_type_name} page: {$page} max_page: {$max_page} child_i: $i vod_id: {$data['vod_id']} file json exists! jump~\n";
            }
            continue;
        }

        $html = getHtml($content_url);

        if (!preg_match('/player_aaaa.*"url":"(http.*m3u8)","url_next/', $html, $ret)) {
            echo "[error] vod_play preg match error! vod_id: {$data['vod_id']}\n";
            continue;
        }

        $data['media'] = str_replace("\/", "/", $ret[1]);

        if (preg_match('/时间：([ \d\-:]+)/', $html, $ret)) {
            $data['uptime'] = $ret[1];
        } else {
            echo "[error] upload time preg match error! vod_id: {$data['vod_id']}\n";
            $data['uptime'] = '';
        }


        print_r($data);
        echo "[info] page: {$page} max_page: {$max_page} child_i: $i ";
        foreach ($data as $key => $value) {
            echo "{$key}: {$value} ";
        }
        echo "\n";

        unset($data['vod_type_name']);
        $data['title'] = base64_encode($data['title']);
        $data['thumd'] = preg_replace("/https?:\/\/[a-zA-Z\d\.]+\/images/", "/images", $data['thumd']);
        $data['thumd'] = base64_encode($data['thumd']);
        $data['media'] = base64_encode($data['media']);

        file_put_contents($file_vod_id_json, json_encode($data, JSON_UNESCAPED_UNICODE));
    }

    return true;
}

function check_image_host(): bool
{
    global $imagehost;
    global $file_imagehost;
    $old_imagehost = @file_get_contents($file_imagehost);
    if ($old_imagehost != $imagehost) {
        echo "[debug] images host update! new: {$imagehost} old: {$old_imagehost}\n";
        file_put_contents($file_imagehost, $imagehost);
        return true;
    }
    return false;
}

function start()
{
    $vod_list = [
        15 => "国产视频",
        9 => "有码中文字幕",
        8 => "无码中文字幕",
        10 => "日本无码",
        7 => "日本有码",
        21 => "欧美高清",
        22 => "动漫剧情",
    ];
    global $vod_list_max;
    global $file_vod;
    global $wxpusher_apptoken;
    $prev_vod_list_max = [];
    $vod_str = @file_get_contents($file_vod);
    if ($vod_str) {
        $prev_vod_list_max = json_decode($vod_str, true);
    }

    file_put_contents($file_vod, json_encode($vod_list_max));

    $max_page = 0;

    foreach ($vod_list as $vod_type_id => $vod_type_name) {
        if (isset($vod_list_max[$vod_type_id])) {
            if (isset($prev_vod_list_max[$vod_type_id])) { // 查看是否存在历史
                if ($vod_list_max[$vod_type_id]['num'] > $prev_vod_list_max[$vod_type_id]['num']) { // 有更新
                    $vod_list_max[$vod_type_id]['page'] = ceil(($vod_list_max[$vod_type_id]['num'] - $prev_vod_list_max[$vod_type_id]['num']) / 40);
                } else {
                    $vod_list_max[$vod_type_id]['page'] = 0;
                }
            }
            if ($vod_list_max[$vod_type_id]['page'] > $max_page) {
                $max_page = $vod_list_max[$vod_type_id]['page'];
            }
        }
    }

    if ($max_page > 0) {
        for ($i = 1; $i <= $max_page; $i++) {
            $list_page = $i;
            foreach ($vod_list as $vod_type_id => $vod_type_name) {
                if (isset($vod_list_max[$vod_type_id]) && $list_page <= $vod_list_max[$vod_type_id]['page']) {
                    getListArr($vod_type_id, $vod_type_name, $list_page, $max_page);
                }
            }
        }
        check_image_host();
        system('php out.php');
        shell_exec('curl -v "https://wxpusher.zjiecode.com/api/send/message/?appToken=' . $wxpusher_apptoken . '&content=hsckUpdate&topicId=10033"');
    } else if (check_image_host()) {
        system('php out.php');
        shell_exec('curl -v "https://wxpusher.zjiecode.com/api/send/message/?appToken=' . $wxpusher_apptoken . '&content=hsckImageUrlUpdate&uid=UID_xKkkEccqH4wC2CqOY48uCMYZqVWU"');
    } else {
        echo "no update!\n";
        shell_exec('curl -v "https://wxpusher.zjiecode.com/api/send/message/?appToken=' . $wxpusher_apptoken . '&content=hsckNoUpdate&uid=UID_xKkkEccqH4wC2CqOY48uCMYZqVWU"');
    }
}

if (!getenv('WXPUSHER_APPTOKEN')) {
    echo "[error] get out! FUCK YOU!\n";
    exit(0);
}

$wxpusher_apptoken = getenv('WXPUSHER_APPTOKEN');

if (!checkHost()) {
    echo "[error] check host error! script stop\n";
    global $wxpusher_apptoken;
    shell_exec('curl -v "https://wxpusher.zjiecode.com/api/send/message/?appToken=' . $wxpusher_apptoken . '&content=hsckCheckHostError&uid=UID_xKkkEccqH4wC2CqOY48uCMYZqVWU"');
    exit(0);
}

start();

var_dump('bin.php run over!');
