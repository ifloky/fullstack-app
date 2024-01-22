const express = require('express');
const router = express.Router();

router.post('/', (req, res) => "DA");
router.get('/', (req, res) => "DA" + req);


module.exports = router;
