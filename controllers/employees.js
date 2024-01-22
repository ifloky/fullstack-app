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

    const employee = await prisma.employee.create({
      data: {
        ...data,
        userId: req.user.id
      }
    });

    return res.status(204).json(employee)

  } catch (error) {

    return res.status(500).json({ message: "Something went wrong" })

  }
}

const remove = async (req, res) => {
  const {id} = req.body;
  try {

    await prisma.employee.delete({
      where: {
        id
      }
    })
    return res.status(204).json({ message: "Deleted" })

  } catch (error) {

    return res.status(500).json({ message: "Can't deleted employee" })

  }
}


const edit = async (req, res) => {
  const data = req.body;
  const id = data.id;
  try {

    await prisma.employee.update({
      where: {
        id
      },
      data
    })
    return res.status(200).json({ message: "Edited" })

  } catch (error) {

    return res.status(500).json({ message: "Can't edited employee" })

  }
}

const employee = async (req, res) => {
  const {id} = req.params;

  try {

    const employee = await prisma.employee.findUnique({
      where: {
        id
      }
    })
    return res.status(200).json(employee)

  } catch (error) {

    return res.status(500).json({ message: "Not found employee" })

  }
}


module.exports = {
  all,
  add,
  remove,
  edit,
  employee
}