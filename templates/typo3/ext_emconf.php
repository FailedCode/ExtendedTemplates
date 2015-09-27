<?php

$EM_CONF[$_EXTKEY] = array(
	'title' => '${extension_name}',
	'description' => '',
	'category' => 'plugin',
	'author' => '${author_name}',
	'author_email' => '${author_email}',
	'author_company' => '${author_company}',
	'shy' => '',
	'state' => 'alpha',
	'uploadfolder' => 1,
	'modify_tables' => '',
	'clearCacheOnLoad' => 0,
	'lockType' => '',
	'version' => '1.0.0',
	'constraints' => array(
		'depends' => array(
			'typo3' => '6.2.2-7.1.99'
		),
		'conflicts' => array(),
		'suggests' => array(),
	),
);
