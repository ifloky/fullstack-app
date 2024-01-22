const { prisma } = require('../prisma/prisma-client');

const all = async (req, res) => {
  try {
    const employees = await prisma.employee.findMany();

    return res.status(200).json(employees)
  } catch (error) {
    return res.status(500).json({ message: "Can't get employees" })
  }
}

const add = async (req, res) => {
  try {
    const data = req.body;

    if (!data.firstName || !data.lastName || !data.address || !data.age) {
      return res.status(400).json({ message: "all fields are required" })
    }

    await prisma.employee.create({
      data: {
        ...data,
        userId: req.user.id
      }
    });

    return res.status(200).json({ message: "employee is created" + employee })

  } catch (error) {

    return res.status(500).json({ message: "Something went wrong" })

  }
}

module.exports = {
  all,
  add
}