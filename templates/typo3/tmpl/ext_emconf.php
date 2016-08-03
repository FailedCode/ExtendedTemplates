<?php

$EM_CONF[$_EXTKEY] = array(
	'title' => '${extension_name}',
	'description' => '',
	'category' => 'plugin',
	'author' => '${author_name}',
	'author_email' => '${author_email}',
	'author_company' => '${author_company}',
	'shy' => '',
	'priority' => '',
	'module' => '',
	'state' => 'alpha',
	'internal' => '',
	'uploadfolder' => 0,
	'createDirs' => '',
	'modify_tables' => '',
	'clearCacheOnLoad' => 0,
	'lockType' => '',
	'version' => '',
	'constraints' => array(
		'depends' => array(
			'extbase' => '6.0',
			'fluid' => '6.0',
			'typo3' => '6.0'
		),
		'conflicts' => array(
		),
		'suggests' => array(
		),
	),
);
